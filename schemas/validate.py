#!/usr/bin/env python3
"""
CROWDShield venue graph validator.

Two-stage validation, because JSON Schema alone is not sufficient for a safety
configuration:

  STAGE 1  Structural validation against the JSON Schema (Draft 2020-12).
  STAGE 2  Cross-reference and physical-plausibility integrity checks that JSON
           Schema cannot express - there are no foreign keys, no sibling-value
           comparisons, and no graph reachability in JSON Schema.

Stage 2 is not optional polish. A venue graph can be perfectly schema-valid and
still describe a trap (no reachable exit), silently suppress every alert (an
over-stated area_sqm), or make the bottleneck engine confidently wrong (a
critical_threshold below base_capacity). Those are the failures that matter.

Also recomputes and patches topology_version.content_hash, and the
topology_binding.content_hash of any paired telemetry frame, so that the
hash-binding discipline described in the schemas is real rather than decorative.

Usage:
    python validate.py                 # validate + integrity check
    python validate.py --write-hashes  # also patch content hashes in place
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import deque
from pathlib import Path

VALIDATOR_BACKEND = "jsonschema (reference implementation)"
try:
    from jsonschema import Draft202012Validator  # type: ignore
except ImportError:
    # jsonschema < 4.18 has no Draft 2020-12 support. Fall back to the bundled
    # subset validator so the schemas are still genuinely verified rather than
    # assumed correct. See _draft202012_subset.py for exactly what it covers.
    from _draft202012_subset import Validator as _Subset, assert_supported

    VALIDATOR_BACKEND = "bundled subset validator (_draft202012_subset.py)"

    class Draft202012Validator:  # type: ignore[no-redef]
        def __init__(self, schema):
            self._v = _Subset(schema)
            self._schema = schema

        @staticmethod
        def check_schema(schema):
            unknown = assert_supported(schema)
            if unknown:
                raise ValueError(
                    "schema uses keywords the bundled validator does not implement, "
                    "so a pass would be misleading:\n  " + "\n  ".join(unknown)
                )

        def iter_errors(self, instance):
            for msg in self._v.iter_errors(instance):
                loc, _, text = msg.partition(": ")
                yield _Err(text, loc)

        def is_valid(self, instance):
            return self._v.is_valid(instance)

    class _Err:
        def __init__(self, message, loc):
            self.message = message
            self.path = [p for p in loc.strip("/").split("/") if p and p != "<root>"]

ROOT = Path(__file__).resolve().parent
TOPOLOGY_SCHEMA = ROOT / "venue-graph.schema.json"
TELEMETRY_SCHEMA = ROOT / "venue-telemetry-frame.schema.json"
TOPOLOGY_SAMPLE = ROOT / "examples" / "mini-venue.topology.json"
TELEMETRY_SAMPLE = ROOT / "examples" / "mini-venue.telemetry-frame.json"

SENTINEL_HASH = "sha256:" + "0" * 64

# Modes in which an edge carries people at all. `restricted` still flows,
# at a derated capacity, so it counts as traversable for reachability.
FLOWING_MODES = {"open", "restricted", "one_way_forward", "one_way_reverse"}


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def canonical_hash(doc: dict) -> str:
    """Hash over the canonicalised document with the hash field itself removed."""
    scrubbed = copy.deepcopy(doc)
    scrubbed.get("topology_version", {}).pop("content_hash", None)
    payload = json.dumps(scrubbed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


_NUMERIC_ARRAY = re.compile(r"\[\s*(-?[\d.eE+]+\s*(?:,\s*-?[\d.eE+]+\s*)*)\]")


def dump_readable(doc: dict, path: Path) -> None:
    """
    Write indented JSON, but keep coordinate pairs on one line.

    Default indent=2 explodes every [x, y] into six lines, which makes polygon
    geometry unreadable and unreviewable. Geometry that a human cannot review is
    geometry nobody checks, and area_sqm errors are the most alert-suppressing
    mistake available in this schema - so legibility here is a safety property,
    not cosmetics.
    """
    text = json.dumps(doc, indent=2, ensure_ascii=False)
    prev = None
    while prev != text:  # repeat to collapse nested coordinate rings
        prev = text
        text = _NUMERIC_ARRAY.sub(
            lambda m: "[" + ", ".join(m.group(1).split()).replace(",,", ",").rstrip(",") + "]",
            text,
        )
    with path.open("w", encoding="utf-8") as fh:
        fh.write(text + "\n")


# ----------------------------------------------------------------------------
# Stage 2: integrity checks
# ----------------------------------------------------------------------------

def check_integrity(topo: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    zones = topo.get("zones", [])
    edges = topo.get("edges", [])
    controls = topo.get("control_points", [])

    # --- 1. identifier uniqueness -------------------------------------------
    def dupes(items, key):
        seen, dup = set(), set()
        for it in items:
            v = it.get(key)
            if v in seen:
                dup.add(v)
            seen.add(v)
        return dup

    for coll, key, label in (
        (zones, "zone_id", "zone"),
        (edges, "edge_id", "edge"),
        (controls, "control_point_id", "control point"),
    ):
        for d in sorted(dupes(coll, key)):
            errors.append(f"[1] duplicate {label} id: {d!r}")

    zone_ids = {z["zone_id"] for z in zones}
    edge_ids = {e["edge_id"] for e in edges}
    edge_by_id = {e["edge_id"]: e for e in edges}

    # --- 2. edge endpoints resolve ------------------------------------------
    for e in edges:
        for end in ("source_zone", "target_zone"):
            if e.get(end) not in zone_ids:
                errors.append(f"[2] edge {e['edge_id']!r} {end}={e.get(end)!r} does not resolve to a zone")
        if e.get("source_zone") == e.get("target_zone"):
            errors.append(f"[2] edge {e['edge_id']!r} is a self-loop; flow conservation is undefined")

    # --- 3. control_point.governs_edges resolves ----------------------------
    for cp in controls:
        for eid in cp.get("governs_edges", []):
            if eid not in edge_ids:
                errors.append(
                    f"[3] control point {cp['control_point_id']!r} governs unknown edge {eid!r}"
                )
        if cp.get("actuation") == "fixed":
            warnings.append(
                f"[3] control point {cp['control_point_id']!r} has actuation=fixed; "
                "it must never appear in a recommendation (SPEC FR-063)"
            )
        default = cp.get("default_mode")
        supported = cp.get("supported_modes")
        if supported and default not in supported:
            errors.append(
                f"[3] control point {cp['control_point_id']!r} default_mode={default!r} "
                f"is not in supported_modes {supported}"
            )

    # --- 4. capacity ordering and plausibility ------------------------------
    for z in zones:
        base = z.get("base_capacity_persons")
        crit = z.get("critical_threshold_persons")
        area = z.get("area_sqm")
        if None not in (base, crit) and crit < base:
            errors.append(
                f"[4] zone {z['zone_id']!r} critical_threshold_persons ({crit}) "
                f"< base_capacity_persons ({base}); Time-To-Critical would count down to a value "
                "already exceeded under normal operation"
            )
        if None not in (crit, area) and area > 0:
            crit_density = crit / area
            if crit_density > 8:
                errors.append(
                    f"[4] zone {z['zone_id']!r} implies a critical density of {crit_density:.2f}/m2, "
                    "which is beyond any plausible survivable standing density; check area_sqm"
                )
            elif crit_density < 1.0:
                # Not merely conservative - almost certainly a data-entry error in
                # area_sqm or critical_threshold_persons. No real venue has a crush
                # threshold below 1 person/m2, and an over-stated area silently
                # UNDER-reports measured density, which suppresses alerts rather
                # than raising them. That is the dangerous direction of the error,
                # so it is a hard failure.
                errors.append(
                    f"[4] zone {z['zone_id']!r} implies a critical density of only "
                    f"{crit_density:.3f}/m2 ({crit} persons over {area} m2), which is below any "
                    "plausible crush threshold; area_sqm or critical_threshold_persons is wrong. "
                    "An over-stated area under-reports density and silently suppresses alerts"
                )
            elif crit_density > 6:
                warnings.append(
                    f"[4] zone {z['zone_id']!r} implies a critical density of {crit_density:.2f}/m2, "
                    "which is very high; confirm area_sqm excludes permanent obstructions"
                )
            elif crit_density < 1.5:
                warnings.append(
                    f"[4] zone {z['zone_id']!r} implies a critical density of only "
                    f"{crit_density:.2f}/m2; unusually conservative, expect frequent alerts"
                )
            if base is not None:
                base_density = base / area
                if base_density > 5:
                    errors.append(
                        f"[4] zone {z['zone_id']!r} base_capacity_persons implies a NORMAL "
                        f"operating density of {base_density:.2f}/m2, which is already in the "
                        "crush band; this would treat a dangerous state as routine"
                    )

        # density band monotonicity (JSON Schema cannot compare siblings)
        bands = z.get("density_bands") or {}
        ordered = [
            ("comfortable_max_persons_per_sqm", bands.get("comfortable_max_persons_per_sqm")),
            ("constrained_max_persons_per_sqm", bands.get("constrained_max_persons_per_sqm")),
            ("dense_max_persons_per_sqm", bands.get("dense_max_persons_per_sqm")),
            ("critical_min_persons_per_sqm", bands.get("critical_min_persons_per_sqm")),
        ]
        present = [(n, v) for n, v in ordered if v is not None]
        for (n1, v1), (n2, v2) in zip(present, present[1:]):
            if v2 < v1:
                errors.append(
                    f"[4] zone {z['zone_id']!r} density_bands not non-decreasing: {n1}={v1} > {n2}={v2}"
                )
        if bands and bands.get("calibration_status") == "uncalibrated_default":
            warnings.append(
                f"[4] zone {z['zone_id']!r} density_bands are uncalibrated defaults; "
                "the UI must label them as such (SPEC FR-059)"
            )

        # closed polygon rings
        geom = z.get("geometry")
        if geom:
            for i, ring in enumerate(geom.get("coordinates", [])):
                if ring and ring[0] != ring[-1]:
                    errors.append(
                        f"[4] zone {z['zone_id']!r} geometry ring {i} is not closed "
                        "(first coordinate must repeat as last)"
                    )

    # --- 5. derived adjacency agrees with the edge list ---------------------
    expected_in: dict[str, set[str]] = {z: set() for z in zone_ids}
    expected_out: dict[str, set[str]] = {z: set() for z in zone_ids}
    for e in edges:
        if e.get("source_zone") in expected_out:
            expected_out[e["source_zone"]].add(e["edge_id"])
        if e.get("target_zone") in expected_in:
            expected_in[e["target_zone"]].add(e["edge_id"])

    for z in zones:
        zid = z["zone_id"]
        for field, expected in (("incoming_edges", expected_in), ("outgoing_edges", expected_out)):
            if field in z:
                declared = set(z[field])
                if declared != expected.get(zid, set()):
                    errors.append(
                        f"[5] zone {zid!r} {field} is stale: declared {sorted(declared)}, "
                        f"edge list implies {sorted(expected.get(zid, set()))}"
                    )

    # derived inverse index on edges
    expected_ctl: dict[str, set[str]] = {eid: set() for eid in edge_ids}
    for cp in controls:
        for eid in cp.get("governs_edges", []):
            if eid in expected_ctl:
                expected_ctl[eid].add(cp["control_point_id"])
    for e in edges:
        if "controlled_by" in e:
            declared = set(e["controlled_by"])
            if declared != expected_ctl.get(e["edge_id"], set()):
                errors.append(
                    f"[5] edge {e['edge_id']!r} controlled_by is stale: declared {sorted(declared)}, "
                    f"control points imply {sorted(expected_ctl.get(e['edge_id'], set()))}"
                )

    # --- 6. egress terminal exists and is reachable from everywhere ---------
    terminals = {z["zone_id"] for z in zones if z.get("is_egress_terminal")}
    if not terminals:
        errors.append(
            "[6] no zone has is_egress_terminal=true; the egress-adequacy signal "
            "(SPEC §9 family B) cannot be computed and the graph describes a trap"
        )
    else:
        # reverse traversal from terminals, honouring declared default modes
        rev: dict[str, set[str]] = {z: set() for z in zone_ids}
        for e in edges:
            mode = (e.get("dynamic_state") or {}).get("mode")
            if mode not in FLOWING_MODES:
                continue
            traversal = e.get("traversal", "bidirectional")
            src, tgt = e.get("source_zone"), e.get("target_zone")
            if src not in zone_ids or tgt not in zone_ids:
                continue
            fwd_ok = traversal in ("bidirectional", "forward_only") and mode != "one_way_reverse"
            rev_ok = traversal in ("bidirectional", "reverse_only") and mode != "one_way_forward"
            if fwd_ok:
                rev[tgt].add(src)
            if rev_ok:
                rev[src].add(tgt)

        seen = set(terminals)
        q = deque(terminals)
        while q:
            cur = q.popleft()
            for prev in rev.get(cur, ()):
                if prev not in seen:
                    seen.add(prev)
                    q.append(prev)

        for zid in sorted(zone_ids - seen):
            errors.append(
                f"[6] zone {zid!r} cannot reach any egress terminal under the declared "
                "default edge states; this venue graph describes a trap"
            )

    # --- 7. edge physical plausibility --------------------------------------
    for e in edges:
        w, mw = e.get("width_meters"), e.get("min_width_meters")
        if None not in (w, mw) and mw > w:
            errors.append(
                f"[7] edge {e['edge_id']!r} min_width_meters ({mw}) exceeds width_meters ({w})"
            )
        cap = e.get("flow_capacity_per_minute")
        gov = mw if mw is not None else w
        if None not in (cap, gov) and gov > 0:
            specific = cap / gov
            if specific > 110:
                errors.append(
                    f"[7] edge {e['edge_id']!r} implies {specific:.0f} persons/min/m of width, "
                    "above any physically attainable specific flow; capacity is over-stated"
                )
            elif specific > 90:
                warnings.append(
                    f"[7] edge {e['edge_id']!r} implies {specific:.0f} persons/min/m, near the "
                    "theoretical maximum; only defensible if measured, not derived"
                )
        basis = e.get("flow_capacity_basis") or {}
        if not basis:
            warnings.append(
                f"[7] edge {e['edge_id']!r} has no flow_capacity_basis; an unexplained capacity "
                "is the documented failure mode of the bottleneck engine (SPEC AI-4)"
            )
        elif basis.get("method") in ("derived_from_width", "engineering_estimate"):
            warnings.append(
                f"[7] edge {e['edge_id']!r} capacity is {basis['method']}, not measured; "
                "bottleneck conclusions inherit that uncertainty"
            )
        if e.get("is_monitored_flow") is not True:
            warnings.append(
                f"[7] edge {e['edge_id']!r} flow is unmonitored; the engine must report UNKNOWN "
                "for it rather than assume it is healthy"
            )

    # --- 8. single-egress zones deserve a hazard override -------------------
    for z in zones:
        zid = z["zone_id"]
        if z.get("is_egress_terminal"):
            continue
        outs = expected_out.get(zid, set())
        flowing = [
            eid for eid in outs
            if (edge_by_id[eid].get("dynamic_state") or {}).get("mode") in FLOWING_MODES
        ]
        if len(flowing) == 1:
            warnings.append(
                f"[8] zone {zid!r} has exactly one flowing egress edge ({flowing[0]!r}); "
                "closing it removes all egress capacity - confirm a hazard override covers this"
            )
        if not flowing:
            errors.append(f"[8] zone {zid!r} has no flowing egress edge under declared default states")

    return errors, warnings


# ----------------------------------------------------------------------------
# Negative tests: the static/telemetry boundary must fail closed
# ----------------------------------------------------------------------------

def negative_tests(schema: dict, topo: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    failures = []

    def expect_invalid(label: str, doc: dict):
        if validator.is_valid(doc):
            failures.append(f"NEGATIVE TEST FAILED - schema accepted an invalid document: {label}")

    # telemetry smuggled into a topology document
    d = copy.deepcopy(topo)
    d["zones"][0]["current_state"] = {
        "observed_at": "2026-08-19T09:14:00Z",
        "provenance": "live_cv",
        "density_persons_per_sqm": 1.85,
        "mean_speed_mps": 0.85,
        "instability_index": 0.2,
    }
    expect_invalid("topology with zone.current_state", d)

    # runtime provenance on a topology default
    d = copy.deepcopy(topo)
    d["edges"][0]["dynamic_state"]["as_of"] = "2026-08-19T09:14:00Z"
    expect_invalid("topology with dynamic_state.as_of", d)

    d = copy.deepcopy(topo)
    d["telemetry_binding"] = {"frame_id": "x", "observed_at": "2026-08-19T09:14:00Z"}
    expect_invalid("topology with telemetry_binding", d)

    # hydrated snapshot missing the things that make it a snapshot
    d = copy.deepcopy(topo)
    d["document_kind"] = "hydrated_snapshot"
    expect_invalid("hydrated_snapshot without telemetry_binding or current_state", d)

    # closed schema must reject typos
    d = copy.deepcopy(topo)
    d["zones"][0]["critical_threshhold_persons"] = 900
    expect_invalid("misspelled property on a zone", d)

    # unit-range guards
    d = copy.deepcopy(topo)
    d["zones"][0]["area_sqm"] = 0
    expect_invalid("zone with area_sqm = 0", d)

    d = copy.deepcopy(topo)
    d["edges"][0]["dynamic_state"]["mode"] = "sort_of_open"
    expect_invalid("edge with an unknown dynamic_state.mode", d)

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-hashes", action="store_true",
                    help="recompute and patch content hashes in place")
    args = ap.parse_args()

    topo_schema = load(TOPOLOGY_SCHEMA)
    tele_schema = load(TELEMETRY_SCHEMA)
    topo = load(TOPOLOGY_SAMPLE)
    tele = load(TELEMETRY_SAMPLE)

    print("=" * 74)
    print("STAGE 0  schema well-formedness (Draft 2020-12)")
    print(f"          backend: {VALIDATOR_BACKEND}")
    print("=" * 74)
    for name, sch in (("venue-graph", topo_schema), ("venue-telemetry-frame", tele_schema)):
        Draft202012Validator.check_schema(sch)
        print(f"  OK    {name}.schema.json is a valid Draft 2020-12 schema")

    print()
    print("=" * 74)
    print("STAGE 1  structural validation of samples")
    print("=" * 74)
    hard_fail = False
    for label, sch, doc in (
        ("mini-venue.topology.json", topo_schema, topo),
        ("mini-venue.telemetry-frame.json", tele_schema, tele),
    ):
        errs = sorted(Draft202012Validator(sch).iter_errors(doc), key=lambda e: list(e.path))
        if errs:
            hard_fail = True
            print(f"  FAIL  {label}")
            for e in errs:
                loc = "/".join(str(p) for p in e.path) or "<root>"
                print(f"          {loc}: {e.message}")
        else:
            print(f"  OK    {label} validates")

    print()
    print("=" * 74)
    print("STAGE 2  cross-reference and physical integrity")
    print("=" * 74)
    errors, warnings = check_integrity(topo)
    for e in errors:
        print(f"  ERROR   {e}")
    for w in warnings:
        print(f"  advisory {w}")
    if errors:
        hard_fail = True
    else:
        print(f"  OK    all integrity checks passed ({len(warnings)} advisories)")

    print()
    print("=" * 74)
    print("STAGE 3  negative tests (the boundary must fail closed)")
    print("=" * 74)
    neg = negative_tests(topo_schema, topo)
    for f in neg:
        print(f"  {f}")
    if neg:
        hard_fail = True
    else:
        print("  OK    7/7 invalid documents correctly rejected")

    print()
    print("=" * 74)
    print("STAGE 4  content hash binding")
    print("=" * 74)
    computed = canonical_hash(topo)
    declared = topo.get("topology_version", {}).get("content_hash")
    bound = tele.get("topology_binding", {}).get("content_hash")
    print(f"  computed  {computed}")
    print(f"  declared  {declared}")
    print(f"  frame     {bound}")

    if args.write_hashes:
        topo["topology_version"]["content_hash"] = computed
        recomputed = canonical_hash(topo)  # excludes the field, so stable
        assert recomputed == computed, "hash must be independent of the hash field"
        tele["topology_binding"]["content_hash"] = computed
        for path, doc in ((TOPOLOGY_SAMPLE, topo), (TELEMETRY_SAMPLE, tele)):
            dump_readable(doc, path)
        print("  patched   topology_version.content_hash and topology_binding.content_hash")
        print("  verified  hash is stable under insertion (excludes its own field)")
    else:
        if declared == SENTINEL_HASH:
            print("  advisory  sentinel hash present; run with --write-hashes to bind")
        elif declared != computed:
            hard_fail = True
            print("  ERROR     declared hash does not match content")
        if bound != declared:
            print("  advisory  frame binding does not match topology hash")

    print()
    print("=" * 74)
    print("RESULT: " + ("FAILED" if hard_fail else "PASSED"))
    print("=" * 74)
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
