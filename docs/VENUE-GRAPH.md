# Venue Graph — Data Architecture Notes

Companion to `schemas/venue-graph.schema.json` and `schemas/venue-telemetry-frame.schema.json`.
Implements SPEC-v1 requirement **N-3**. Consumed by **N-4** (Bottleneck Physics Engine),
SPEC §9 (Risk Engine), SPEC §11 (Recommendation Engine), and **N-5** (counterfactual simulation).

---

## 1. The three-tier state model

The brief asked to separate static physical topology from high-frequency telemetry. Working
through it, there are actually **three** tiers, and the middle one is where designs usually go
wrong:

| Tier | What | Change rate | Where it lives |
|---|---|---|---|
| 1 · Static topology | geometry, `area_sqm`, `width_meters`, capacities, criticality | immutable per event | `venue-graph.schema.json` (`document_kind: topology`) |
| 2 · Operational state | gate open/closed, one-way settings, barricade derate | a handful of transitions per event, operator-driven | `dynamic_state` on edges; authoritative record is the audited transition log |
| 3 · Telemetry | density, mean speed, instability index | multiple per zone per second | `venue-telemetry-frame.schema.json` |

Collapsing Tier 2 into Tier 1 makes the topology mutable mid-event, which destroys the
content-hash guarantee. Collapsing it into Tier 3 loses the distinction between a *measured*
fact and an *asserted* one — a gate's position is asserted by a human and confirmed by a
responder, not observed by a sensor.

The separation is **machine-enforced**, not conventional. `document_kind` drives conditional
subschemas: a `topology` document containing `current_state` fails validation, and a
`hydrated_snapshot` lacking it also fails. Seven negative tests in `validate.py` confirm the
boundary fails closed.

One consequence worth naming: `traversal` (the *designed* physical affordance) is deliberately
separate from `dynamic_state.mode` (the *current* operator setting). A corridor can be
physically bidirectional yet currently set one-way. Conflating them loses the information
needed to know what an operator is allowed to change it *back* to.

---

## 2. How the structure optimises the Bottleneck Physics Engine

N-4 must answer four questions on every evaluation tick. Each schema decision below exists to
make one of them cheap.

### Q1 — "Which connections are saturated?"

Utilisation is `measured_flow / (flow_capacity_per_minute × capacity_derate_factor)`. Every
term is a direct field read on one edge and its state object — no joins, no derivation, no
geometry parsing. Storing capacity explicitly rather than deriving it from `width_meters` at
runtime keeps the hot path arithmetic-free; retaining `width_meters` and `min_width_meters`
anyway means the number stays **auditable**, which matters because AI-4's documented failure
mode is that a wrong capacity produces confidently wrong conclusions. `flow_capacity_basis` is
mandatory for the same reason: the operator is entitled to know whether an alert is driven by a
measured constraint or a guess.

### Q2 — "Where is queue length growing?"

Flow conservation per zone: `Σ incoming_edges − Σ outgoing_edges`. The denormalised
`incoming_edges` / `outgoing_edges` arrays make this a direct index read rather than a scan of
the edge list per zone. Complexity goes from O(V·E) per tick to O(V+E).

At prototype scale (3 zones, 2 edges) this is irrelevant to wall-clock time and the honest
justification is different: it makes the iteration *obviously correct* to a reader, and it lets
consumers that never build their own index — the map renderer, the mobile client — get O(1)
adjacency. At production scale (hundreds of zones across multiple venues) the complexity class
starts to matter.

Denormalising derived data into a source-of-truth artifact is a real hazard, so it is contained:
the fields are `readOnly`, documented as compiler-generated rather than hand-authored, optional
so an author need not maintain them, and **machine-checked** — `validate.py` rebuilds the index
from the edge list and fails on any disagreement. Same treatment for `controlled_by`, the
inverse of `control_point.governs_edges`.

### Q3 — "Is there enough egress?"

This is SPEC §9 signal family B, the signal that distinguishes a merely crowded space from a
trap. It is a reachability query: from zone *Z*, which `is_egress_terminal` zones are reachable
over edges currently in a flowing mode, and what is their summed capacity?

Two schema decisions make this tractable. First, `is_egress_terminal` marks the graph's sinks
explicitly, so reachability has a defined target set. Second — and this is the important one —
egress capacity only changes when a **Tier 2** transition occurs, which happens a handful of
times per event, not on every tick. So reachability is computed once at load and recomputed
**event-driven**, never per-tick. `governs_edges` scopes that recompute: toggling a control point
invalidates exactly the edges it governs, not the whole graph.

`terminal_discharge_capacity_per_minute` exists because an exit discharging onto a narrow street
is not an infinite sink. Modelling it as one is a standard egress-planning error and would
overstate available egress precisely when that number matters most.

### Q4 — "*Why* is this a bottleneck?"

Cause determines cure, so the engine must distinguish throttled outflow from surging inflow from
counterflow interference. Three fields carry this:

- `measured_flow_per_minute` **and** `measured_flow_per_minute_reverse` as separate values —
  their co-occurrence *is* the definition of counterflow (FR-027), and sustained reverse flow
  where forward is expected is reverse crowd movement (FR-026). A single signed scalar would
  lose this.
- `flow_capacity_per_minute` (nominal) kept **separate from** `capacity_derate_factor` (current).
  This one was validated the hard way: a naive classifier comparing only *effective* utilisation
  called the sample's cause "surging inflow," because both edges read ~100% of effective
  capacity. The real cause is the barricade derated to 0.6. The distinguishing signal is that
  the outflow edge is at 100% of effective but only 60% of *nominal* capacity — recoverable
  capacity is being withheld. Keeping both terms is what makes that inference possible, and it
  also directly yields the intervention: restoring the derate.
- `flow_measurement_method`, so an edge whose flow is *inferred* from adjacent occupancy change
  is never presented as equivalent to one that is directly measured, and an unmonitored edge is
  reported as UNKNOWN rather than assumed healthy.

### What makes all four cheap: the payload split

The dominant avoidable cost in a system like this is re-serialising immutable geometry on every
tick. Polygons and capacities are kilobytes-to-megabytes and constant for the event; telemetry
is a few hundred bytes of numbers per zone. Separating the documents means the topology is
parsed and indexed **once**, held immutable, and the per-tick path touches only a small mutable
state map.

That same split is what makes SPEC §7's bandwidth and cost claims true, and what lets the
pipeline buffer through a network outage (FR-140) — a queue of feature frames is cheap to hold;
a queue of venue models is not.

### The binding that keeps it safe

Every telemetry frame carries `topology_binding.content_hash`. Without it, an administrator
editing one capacity mid-event would silently invalidate every cached index and make risk scores
from before and after the edit incomparable, with no way to detect it. A consumer whose loaded
hash differs must refuse the frame or reload. The hash is computed over the canonicalised
document with the hash field itself excluded, so it is stable under its own insertion —
`validate.py` asserts that property rather than assuming it.

---

## 3. What this schema deliberately does *not* hold

Keeping these out is what stops the venue model becoming a god-object and keeps the deterministic
risk core auditable:

- **Derived ratios requiring the topology join** — occupancy ratio, edge utilisation. The rule is
  that a telemetry frame carries what a sensing node can compute *alone*; anything needing the
  join is computed by the consumer.
- **Detections** — bottleneck, blockage, counterflow, surge. Outputs of the Detection layer.
- **Risk score, severity, Time-To-Critical, recommendations.** Outputs of the Risk and
  Recommendation engines.
- **Time series.** Rolling windows belong in a time-series store, not in a graph document.
- **Per-cell density rasters.** Wrong shape for JSON; a separate binary payload.

---

## 4. Validation

`python schemas/validate.py [--write-hashes]`

Four stages: schema well-formedness → structural validation of both samples → cross-reference
and physical integrity → negative tests. Current status: **PASSED**, with 7 advisories (all
uncalibrated-default and derived-capacity notices, which are expected and are exactly what
FR-059 requires the UI to surface).

### Why stage 3 exists

JSON Schema has no foreign keys, no sibling-value comparison, and no graph reachability. A venue
graph can be fully schema-valid and still be dangerously wrong. The integrity pass enforces:

1. identifier uniqueness across zones, edges, control points
2. every `source_zone` / `target_zone` resolves; no self-loops
3. every `governs_edges` entry resolves; `default_mode` ∈ `supported_modes`
4. `critical_threshold_persons ≥ base_capacity_persons`; implied densities physically plausible;
   `density_bands` non-decreasing; polygon rings closed
5. derived adjacency and `controlled_by` agree with the authoritative lists
6. an egress terminal exists and is reachable from every zone under declared default states
7. `min_width ≤ width`; specific flow within attainable limits; capacity basis declared
8. single-egress zones flagged for hazard-override review

An adversarial suite mutates the valid sample 16 ways and confirms all 16 are rejected. That
suite earned its keep: it initially caught only 12/16, exposing that an over-stated `area_sqm`
passed as a mere advisory. That is the **most dangerous error direction in this schema** — an
inflated area under-reports density and *suppresses* alerts rather than raising them — so an
implied critical density below 1.0 persons/m² is now a hard failure, as is a `base_capacity`
implying a normal operating density already in the crush band.

### On the validator backend

`validate.py` prefers `jsonschema >= 4.18`. Where no package registry is reachable it falls back
to `_draft202012_subset.py`, a bundled validator covering exactly the keyword subset these
schemas use. That module is a verification aid, not a general-purpose validator: it documents
what it implements, and `assert_supported()` walks each schema and **raises** on any keyword it
does not understand, so a coverage gap fails loudly instead of producing a false pass. CI should
use `ajv` or `jsonschema>=4.18` once network access is available.

---

## 5. Open decisions this schema does not make

Deferred to SPEC-v1 §19, deliberately:

- storage — versioned file vs database, and whether the compiled index is cached
- the `instability_index` formula (the sample uses `density × velocity_dispersion` purely for
  internal consistency; thresholds throughout are `uncalibrated_default`)
- evaluation interval and staleness threshold
- initial `density_bands` breakpoints and which published pedestrian level-of-service bands to
  adopt as a starting point
- whether zones subdivide into a density grid for sub-zone hotspot localisation
- multi-level venues: whether `level` is sufficient or vertical circulation needs richer modelling
