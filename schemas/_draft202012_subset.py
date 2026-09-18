#!/usr/bin/env python3
"""
Minimal JSON Schema Draft 2020-12 validator covering the keyword subset used by
the CROWDShield schemas.

WHY THIS EXISTS. This module is a verification aid, not a general-purpose
validator. The reference implementations (`jsonschema>=4.18` for Python, `ajv`
for Node) are the right tools and CI should use them. This exists so the schemas
in this repository can be verified in an environment without package-registry
access, rather than being shipped unvalidated.

KEYWORDS IMPLEMENTED
    core        $ref (local JSON pointers only), $defs, boolean schemas
    applicators properties, additionalProperties, items, prefixItems,
                allOf, anyOf, oneOf, not, if/then/else
    assertions  type, enum, const, required,
                minLength, maxLength, pattern,
                minimum, maximum, exclusiveMinimum, exclusiveMaximum,
                minItems, maxItems, uniqueItems,
                format (date-time only, asserted rather than annotated)

DELIBERATELY NOT IMPLEMENTED
    unevaluatedProperties / unevaluatedItems  (the repo schemas use closed
        `additionalProperties: false` instead, so annotation collection is
        not required)
    $dynamicRef / $dynamicAnchor, remote $ref resolution, contains/minContains,
    dependentSchemas / dependentRequired, patternProperties, propertyNames,
    multipleOf, content* keywords

If a schema in this repository starts using a keyword from the second list,
this module will silently ignore it. `assert_supported()` guards against that
by walking a schema and reporting any keyword it does not understand, so the
gap fails loudly instead of producing a false pass.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterator

__all__ = ["Validator", "assert_supported", "SUPPORTED", "IGNORED_ANNOTATIONS"]

# Annotation-only keywords: present, meaningful to humans, no assertion effect.
IGNORED_ANNOTATIONS = {
    "$schema", "$id", "$comment", "$anchor",
    "title", "description", "default", "examples",
    "readOnly", "writeOnly", "deprecated",
}

SUPPORTED = {
    "$ref", "$defs",
    "properties", "additionalProperties", "items", "prefixItems",
    "allOf", "anyOf", "oneOf", "not", "if", "then", "else",
    "type", "enum", "const", "required",
    "minLength", "maxLength", "pattern",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "minItems", "maxItems", "uniqueItems",
    "format",
} | IGNORED_ANNOTATIONS

_RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})$"
)

_TYPES: dict[str, tuple[type, ...] | str] = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
    "number": "number",
    "integer": "integer",
}


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _type_ok(value: Any, name: str) -> bool:
    expected = _TYPES.get(name)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        return isinstance(value, float) and value.is_integer()
    if expected is bool:
        return isinstance(value, bool)
    if expected is type(None):
        return value is None
    # int is not a valid instance of "string"; bool is a subclass of int so guard
    if expected is str:
        return isinstance(value, str)
    return isinstance(value, expected)  # type: ignore[arg-type]


def assert_supported(schema: Any, path: str = "#") -> list[str]:
    """Walk a schema and report keywords this validator does not implement."""
    unknown: list[str] = []
    if isinstance(schema, bool) or not isinstance(schema, dict):
        return unknown
    for key, sub in schema.items():
        if key not in SUPPORTED:
            unknown.append(f"{path}: unsupported keyword {key!r}")
        if key in ("properties", "$defs"):
            if isinstance(sub, dict):
                for name, s in sub.items():
                    unknown += assert_supported(s, f"{path}/{key}/{name}")
        elif key in ("allOf", "anyOf", "oneOf", "prefixItems"):
            if isinstance(sub, list):
                for i, s in enumerate(sub):
                    unknown += assert_supported(s, f"{path}/{key}/{i}")
        elif key in ("items", "not", "if", "then", "else", "additionalProperties"):
            unknown += assert_supported(sub, f"{path}/{key}")
    return unknown


class Validator:
    """Validates instances against a single self-contained schema document."""

    def __init__(self, schema: dict | bool):
        self.root = schema

    # -- $ref resolution (local pointers only) -------------------------------
    def _resolve(self, ref: str) -> Any:
        if not ref.startswith("#"):
            raise ValueError(f"only local $ref supported, got {ref!r}")
        node: Any = self.root
        pointer = ref[1:]
        if not pointer:
            return node
        for raw in pointer.lstrip("/").split("/"):
            token = raw.replace("~1", "/").replace("~0", "~")
            if isinstance(node, list):
                node = node[int(token)]
            else:
                node = node[token]
        return node

    def is_valid(self, instance: Any) -> bool:
        for _ in self.iter_errors(instance):
            return False
        return True

    def iter_errors(self, instance: Any) -> Iterator[str]:
        yield from self._validate(instance, self.root, "")

    # -- core ----------------------------------------------------------------
    def _validate(self, inst: Any, schema: Any, loc: str) -> Iterator[str]:
        where = loc or "<root>"

        if schema is True:
            return
        if schema is False:
            yield f"{where}: property/value is not permitted here"
            return
        if not isinstance(schema, dict):
            return

        if "$ref" in schema:
            # Draft 2020-12: $ref applies alongside its siblings.
            yield from self._validate(inst, self._resolve(schema["$ref"]), loc)

        if "type" in schema:
            types = schema["type"]
            types = [types] if isinstance(types, str) else types
            if not any(_type_ok(inst, t) for t in types):
                yield f"{where}: expected type {'/'.join(types)}, got {type(inst).__name__}"
                return

        if "const" in schema and _canon(inst) != _canon(schema["const"]):
            yield f"{where}: must equal {schema['const']!r}"
        if "enum" in schema:
            allowed = {_canon(v) for v in schema["enum"]}
            if _canon(inst) not in allowed:
                yield f"{where}: {inst!r} is not one of {schema['enum']!r}"

        if isinstance(inst, str):
            yield from self._string(inst, schema, where)
        if isinstance(inst, (int, float)) and not isinstance(inst, bool):
            yield from self._number(inst, schema, where)
        if isinstance(inst, list):
            yield from self._array(inst, schema, loc, where)
        if isinstance(inst, dict):
            yield from self._object(inst, schema, loc, where)

        for key in ("allOf", "anyOf", "oneOf"):
            if key not in schema:
                continue
            results = [
                list(self._validate(inst, sub, loc)) for sub in schema[key]
            ]
            passed = sum(1 for r in results if not r)
            if key == "allOf":
                for r in results:
                    yield from r
            elif key == "anyOf" and passed == 0:
                yield f"{where}: does not match any of the {len(results)} anyOf subschemas"
            elif key == "oneOf" and passed != 1:
                yield f"{where}: must match exactly one oneOf subschema, matched {passed}"

        if "not" in schema and self._ok(inst, schema["not"], loc):
            yield f"{where}: must not match the `not` subschema"

        if "if" in schema:
            branch = "then" if self._ok(inst, schema["if"], loc) else "else"
            if branch in schema:
                yield from self._validate(inst, schema[branch], loc)

    def _ok(self, inst: Any, schema: Any, loc: str) -> bool:
        for _ in self._validate(inst, schema, loc):
            return False
        return True

    # -- per-type assertions -------------------------------------------------
    def _string(self, inst: str, schema: dict, where: str) -> Iterator[str]:
        if "minLength" in schema and len(inst) < schema["minLength"]:
            yield f"{where}: shorter than minLength {schema['minLength']}"
        if "maxLength" in schema and len(inst) > schema["maxLength"]:
            yield f"{where}: longer than maxLength {schema['maxLength']}"
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            yield f"{where}: {inst!r} does not match pattern {schema['pattern']!r}"
        if schema.get("format") == "date-time" and not _RFC3339.match(inst):
            yield f"{where}: {inst!r} is not an RFC 3339 date-time"

    def _number(self, inst: float, schema: dict, where: str) -> Iterator[str]:
        if "minimum" in schema and inst < schema["minimum"]:
            yield f"{where}: {inst} < minimum {schema['minimum']}"
        if "maximum" in schema and inst > schema["maximum"]:
            yield f"{where}: {inst} > maximum {schema['maximum']}"
        if "exclusiveMinimum" in schema and inst <= schema["exclusiveMinimum"]:
            yield f"{where}: {inst} <= exclusiveMinimum {schema['exclusiveMinimum']}"
        if "exclusiveMaximum" in schema and inst >= schema["exclusiveMaximum"]:
            yield f"{where}: {inst} >= exclusiveMaximum {schema['exclusiveMaximum']}"

    def _array(self, inst: list, schema: dict, loc: str, where: str) -> Iterator[str]:
        if "minItems" in schema and len(inst) < schema["minItems"]:
            yield f"{where}: has {len(inst)} items, minItems {schema['minItems']}"
        if "maxItems" in schema and len(inst) > schema["maxItems"]:
            yield f"{where}: has {len(inst)} items, maxItems {schema['maxItems']}"
        if schema.get("uniqueItems"):
            seen: set[str] = set()
            for item in inst:
                key = _canon(item)
                if key in seen:
                    yield f"{where}: contains duplicate items"
                    break
                seen.add(key)

        prefix = schema.get("prefixItems") or []
        for i, sub in enumerate(prefix):
            if i < len(inst):
                yield from self._validate(inst[i], sub, f"{loc}/{i}")
        if "items" in schema:
            for i in range(len(prefix), len(inst)):
                yield from self._validate(inst[i], schema["items"], f"{loc}/{i}")

    def _object(self, inst: dict, schema: dict, loc: str, where: str) -> Iterator[str]:
        for name in schema.get("required", []):
            if name not in inst:
                yield f"{where}: missing required property {name!r}"

        props = schema.get("properties", {})
        for name, sub in props.items():
            if name in inst:
                yield from self._validate(inst[name], sub, f"{loc}/{name}")

        if "additionalProperties" in schema:
            extra = [k for k in inst if k not in props]
            ap = schema["additionalProperties"]
            for name in extra:
                if ap is False:
                    yield f"{where}: unexpected property {name!r} (schema is closed)"
                else:
                    yield from self._validate(inst[name], ap, f"{loc}/{name}")
