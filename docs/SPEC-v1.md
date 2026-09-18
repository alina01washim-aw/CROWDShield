# CROWDShield — Product Requirements Specification

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | 2026-08-19 |
| Status | Baseline for implementation. Changes require a version bump. |
| Primary source of truth | TechNova / ESSPL **"Problem Statement 1 — CrowdShield: An AI-Powered Early Warning System for Preventing Crowd Stampedes"** (4pp, © 2026 TechNova) |
| Scope of this document | Understanding and formal product definition only. No implementation decisions beyond those stated in §19 as open. |

## Provenance legend

Every requirement in this document carries a provenance tag. This is a hard rule, not a convention.

| Tag | Meaning |
|---|---|
| `[O]` | **Official** — explicitly stated in the problem statement |
| `[I]` | **Interpretation** — our technical reading of an official requirement |
| `[N]` | **Innovation** — a CROWDShield addition we are deliberately choosing to make |

Nothing tagged `[I]` or `[N]` may be presented to judges, in documentation, or in UI copy as an official requirement.

## Two framing notes

The project name comes from the problem statement itself. Its official framing is an **early warning system** — not a crowd-control system. We warn, recommend, and support decisions; humans intervene.

One line in the brief does more architectural work than any other: *"minimum hardware dependencies."* Read strictly, it rules out new cameras, wearables, RFID, and drones as prerequisites. That pushes us toward reusing existing CCTV where it exists and treating the phones people already carry as the primary novel sensor. Most design decisions in this document follow from it.

---

## 1. Executive Understanding

**The problem.** Large gatherings in India concentrate enormous numbers of people into limited space over short windows. The problem statement's central observation is not that crowds are dangerous, but that *current practice is reactive*: CCTV, manual supervision, deployment, barricading, and announcements all trigger after abnormal behaviour is visible — and by then the physical conditions that cause a crush are already established. A crowd crush is not an event that starts when people fall; it is the terminal stage of a process that has been building, measurably, for several minutes.

CROWDShield exists to buy back those minutes. It watches the *physical state* of a crowd — how dense it is, how fast and how coherently it is moving, where flow is being throttled — detects the transition from safe flow toward unstable flow, projects that trend forward, and hands authorities a specific, justified intervention while intervention is still cheap. The problem statement quantifies the ambition: an alert roughly ten minutes before a dangerous crush develops.

**Who uses it.** A control-room operator or incident commander (in the brief's framing, a district administration, so: police and civil administration, not only private venue security), field staff on the ground who actually execute interventions, and attendees carrying phones who both receive warnings and supply movement signal.

**What decisions it helps them make.** The brief names them directly, and these are the acceptance test for the whole product: where is density rising abnormally; which locations are becoming bottlenecks; is there crush risk in the next few minutes; which evacuation route is safest; how should security personnel be redistributed; which gates should be opened or closed; what should be announced to reduce panic. Every one of these is an *action* question, not a *statistics* question. A system that answers "density in Zone D is 4.2/m²" has not answered any of them.

**What makes it different from a conventional crowd dashboard.** Five things, in order of importance.

A conventional dashboard reports density. CROWDShield's risk core is built on the insight that density alone is a weak predictor of crush — a dense, slow, uniformly-flowing crowd can be stable for hours, while a moderately dense crowd with high variance in individual velocities and opposing flows is on the edge. The crowd-safety literature (notably Helbing and colleagues' analysis of the 2006 Jamarat disaster) associates crush onset with a transition from laminar flow to stop-and-go waves to "crowd turbulence," and finds that a *crowd pressure* quantity combining local density with velocity variance rises before disaster while density alone plateaus. We therefore measure flow instability, not just headcount. **This is the single most defensible technical differentiator available in this problem space.**

Second, a conventional dashboard reports the present. CROWDShield outputs a **Time-To-Critical** estimate — a countdown in minutes derived from current density, growth rate, and egress capacity — because "risk of crush in the next few minutes" is a question about the future and deserves a number with an uncertainty band, not a colour.

Third, a conventional dashboard raises an alarm. CROWDShield produces a *ranked, feasibility-checked, simulated intervention* with its projected effect, and closes the loop by tracking whether the intervention was executed and whether risk actually fell.

Fourth, a conventional dashboard trusts itself. CROWDShield attaches confidence to every output, degrades that confidence visibly when inputs are sparse or stale, marks simulated data as simulated on screen, and reports its own false-alarm rate back to the operator.

Fifth, a conventional dashboard needs infrastructure. CROWDShield is designed to produce useful output with zero new hardware, and to keep producing it when the network fails.

---

## 2. Official Problem Requirements

Everything in this section is drawn from the problem statement. No additions.

### 2.1 Framing and objective

- Design an affordable, scalable, AI-powered **mobile and cloud-based** solution capable of predicting potential stampede situations **before** they occur.
- Leverage present software innovations to create a **low-cost** solution, easily deployed with **minimum hardware dependencies**.
- Transform crowd management from reactive monitoring into predictive public safety.
- Stated success vision: alert a district administration **~10 minutes before** a dangerous crowd crush develops, enabling proactive redirection, additional exits, personnel deployment, and timely announcements.
- The solution must answer: where is density increasing abnormally; which locations are becoming bottlenecks; is there crowd-crush risk within the next few minutes; which evacuation route is safest; how should authorities redistribute security personnel; which gates should be opened or temporarily closed; what announcements should be made to reduce panic.

### 2.2 Monitoring

- Estimate crowd density.
- Estimate crowd movement speed.
- Identify congestion hotspots.
- Track crowd flow directions.

### 2.3 Detection

- Detect unusual crowd behaviour.
- Identify bottlenecks.

### 2.4 Prediction

- Possible crowd crush.
- Stampede likelihood.
- Panic propagation.
- Sudden crowd surge.
- Reverse crowd movement.
- Route blockage.
- High-risk zones within the venue *before they become dangerous*.

### 2.5 Recommendations

Stated as "actionable interventions to pacify the situation":

- Suggest opening alternate exits.
- Close entry gates.
- Redirect incoming visitors.
- Deploy additional security staff.
- Broadcast multilingual public announcements through mobile and social channels.
- Change barricade configuration.
- Recommend one-way pedestrian flow.
- Trigger multilingual public announcements.

### 2.6 Command Dashboard (control room)

- Live event map.
- Crowd heat map.
- Risk zones.
- Crowd trend analytics.

### 2.7 Mobile Application (companion app for citizens)

- Incident notifications.
- Live multilingual congestion alerts.
- Location-based warnings.
- Incident reporting.

### 2.8 Constraints to be considered

- Limited infrastructure.
- Low-cost deployment.
- Network outages.
- High scalability.
- Data privacy.
- Real-time performance.
- False alarm reduction.
- Ease of use by authorities.

### 2.9 Bonus capabilities

Additional points may be awarded for:

- Digital twin of the venue.
- AI-powered simulation of crowd movement.
- Voice-enabled command center.
- Multilingual AI assistant.
- Generative AI for incident summaries.

### 2.10 Two scope observations

`[I]` "Multilingual" appears three times in the *core* requirements (announcements twice, citizen alerts once) and only once in bonuses. Multilingual output is therefore a core requirement, and only the conversational *assistant* is bonus.

`[I]` The brief says "mobile and cloud-based," so a cloud-hosted service with a mobile client is the officially expected shape. Our edge-preprocessing and offline-tolerance work must be positioned as satisfying the network-outage constraint *within* that architecture, not as a replacement for it.

---

## 3. CROWDShield Innovation Layer

Ten additions. Each is scoped to an official requirement it strengthens — none is a detour.

### N-1 · Crowd Instability Index (density × velocity variance)

**Why it matters.** It is the difference between a headcount tool and a crush-prediction tool. Density saturates; instability keeps rising.

**Solves.** "Possible crowd crush," "stampede likelihood," "high-risk zones before they become dangerous."

**Input.** Per-cell density estimate plus a dense velocity field over a short window.

**Output.** Scalar instability value per zone, plus detection of the laminar → stop-and-go → turbulent transition (signature: mean speed falling while density rises, then variance rising while mean speed stays near zero).

**Difficulty.** Medium. The velocity field comes from optical flow, which requires no training data; the arithmetic is straightforward. Calibrating thresholds is the hard part.

**Demo value.** Very high — it lets us show two zones at identical density where one is safe and one is not, which is the most persuasive thirty seconds available to us.

**Overclaiming risk.** Moderate, and manageable. We must say: this is a *proxy* for a published crowd-pressure quantity, computed from estimated fields, with uncalibrated thresholds. We must not say we "detect crowd turbulence" with known accuracy.

### N-2 · Time-To-Critical (TTC)

**Why it matters.** The brief's success criterion is a lead time. A lead time deserves a number.

**Solves.** "Risk of crowd crush within the next few minutes"; the 10-minute vision.

**Input.** Density time series, inflow/outflow rates, zone area and capacity, current instability.

**Output.** Estimated minutes until the zone crosses its critical threshold, with a confidence interval and an explicit "not projected to reach critical" state.

**Difficulty.** Medium. Honest implementation is trend extrapolation with an uncertainty band, not a black box.

**Demo value.** Very high. A visible countdown is the clearest possible expression of "predictive, not reactive."

**Overclaiming risk.** High if handled carelessly. It must always be rendered as a range with a confidence level, must be allowed to say "unknown," and must never be described as a prediction of a stampede — only of a threshold crossing under current trend.

### N-3 · Venue Graph (a lightweight digital twin)

**Why it matters.** One data structure unlocks five features. Model the venue as zones (nodes with area, capacity, criticality) and connections (edges with width, capacity, direction state, open/closed). From this single model we get bottleneck detection by flow conservation, safest-route computation, gate open/close reasoning, propagation simulation, and the digital-twin bonus.

**Solves.** Bottlenecks, route blockage, safest evacuation route, which gates to open/close, panic propagation, digital twin bonus.

**Input.** A one-time venue configuration (hand-authored for the prototype).

**Output.** A queryable topological model with live state on every node and edge.

**Difficulty.** Low to medium — mostly data modelling and an editor.

**Demo value.** High, and it is the backbone that makes several other features possible rather than fake.

**Overclaiming risk.** Low, provided we call it a topological/capacity model and not a 3D digital twin unless we build 3D.

> **Implementation status:** specified in `schemas/venue-graph.schema.json` and `schemas/venue-telemetry-frame.schema.json`. See `docs/VENUE-GRAPH.md`.

### N-4 · Bottleneck Physics Engine

**Why it matters.** A bottleneck has a physical definition — sustained inflow exceeding outflow capacity at a constriction — so it can be *derived* rather than classified. Derived detections are explainable and need no labels.

**Solves.** "Identify bottlenecks," "route blockage," "congestion hotspots."

**Input.** Edge flow rates from the velocity field, node densities, configured capacities.

**Output.** Ranked bottleneck list with severity, queue-growth rate, and cause (throttled outflow vs. surging inflow vs. counterflow interference) — the cause matters because it determines which intervention works.

**Difficulty.** Medium.

**Demo value.** High.

**Overclaiming risk.** Low.

### N-5 · Intervention Preview (counterfactual simulation)

**Why it matters.** This converts the "AI-powered crowd simulation" bonus from a demo toy into decision support, and it is what makes a recommendation trustworthy instead of magic. Before acting, the operator sees the projected risk curve with and without the intervention.

**Solves.** All recommendation requirements, plus the simulation bonus, plus "ease of use by authorities" and "false alarm reduction" — an operator who can see the projected effect is far more willing to act.

**Input.** Venue graph, current state, candidate intervention, inflow assumptions.

**Output.** Projected per-zone risk at T+5 and T+10 for baseline vs. intervention; expected risk reduction.

**Difficulty.** High — this is the most ambitious item on the list.

**Demo value.** Highest of anything in this specification.

**Overclaiming risk.** High. It must be labelled a simulation under stated assumptions, with those assumptions visible, and never presented as a guarantee of outcome.

### N-6 · Differential Immobility Anomaly — "Guardian Mode"

**Why it matters.** It is a genuinely novel signal and it fills a real gap: a person who has fallen or been pinned inside a moving crowd is invisible to density-based monitoring, and is exactly the small disturbance the problem statement identifies as the trigger for escalation. The insight is that it needs to know nothing about the person — only that their movement state diverges from their immediate neighbours'.

**Solves.** "Detect unusual crowd behaviour" at individual granularity; early detection of the localised disturbance that precedes wider incidents.

**Input.** On-device: displacement over a window, pedometer/accelerometer activity level, positional accuracy. From the server: the local zone's crowd movement baseline (median speed and dispersion) over the same window.

**Output.** A **Check-On Request** — a location, an anomaly duration, a confidence value, and an explicit status of `unverified`. Never a diagnosis.

**Difficulty.** Medium technically, high in design care. Background location and motion permissions, battery, and a staged escalation flow are the real work.

**Demo value.** High — it is memorable and clearly original.

**Overclaiming risk.** **The highest in this document, and it needs hard guardrails.** A phone cannot determine a person's physical condition. Someone stationary in a moving crowd may have fallen, or may be buying tea, taking a photo, tying a shoe, on a call, or have set their bag down. GPS is unreliable in exactly the dense, enclosed, urban-canyon environments that matter most.

Four design decisions contain this:

1. **Staged escalation with self-clearance.** Detection first triggers an on-device prompt — "Are you okay?" with a countdown. A single tap clears it. Most false positives die here at zero cost to the control room, and the user keeps control over whether they are reported at all.
2. **Verification framing throughout.** The operator-facing artifact is a task ("check on this location"), never a claim ("person down"). UI copy, API field names, and demo narration all use the same language.
3. **Confidence must be honest.** It falls with poor positional accuracy, with too few sampled neighbours to form a baseline, with stale data, and with indoor conditions. Below a threshold, the anomaly is suppressed rather than shown.
4. **We state the detector's blind spot ourselves.** In an actual crush, *everyone's* velocity approaches zero, so the differential vanishes and this detector goes quiet precisely when danger peaks. That is not a flaw to hide — it is the reason N-1 exists. The two are complementary: N-6 catches isolated distress in moving crowds; N-1 catches the crowd-level condition where N-6 is blind. Presenting this pairing honestly is stronger than presenting either as complete.

Privacy: processed on-device, transmits zone-level position rather than a continuous trace, pseudonymous by default with identity withheld from the control room unless the user shares it or a responder is dispatched, explicit opt-in, easily revocable, short retention. See §12 and FR-130..137.

### N-7 · Explainability Card on every alert

**Why.** Directly serves "ease of use by authorities" and "false alarm reduction." An operator who cannot see why the system is worried will either ignore it or over-trust it.

**Input/Output.** The risk vector in, a ranked contribution breakdown out ("density 4.6/m² contributed 31 points; speed collapse 18; Gate 3 at 98% capacity 14; two corroborated citizen reports 8"). Because our risk function is a transparent weighted composition, these contributions are *exact*, not approximated post-hoc.

**Difficulty.** Low. **Demo value.** High. **Overclaiming risk.** Low.

### N-8 · Alert Adjudication and self-reported precision

**Why.** This is the LEARN step, and it is the only credible answer to "false alarm reduction." Every alert gets closed out by an operator as confirmed / false / unclear. The system then reports its own precision for the event and proposes threshold adjustments for review.

**Difficulty.** Low. **Demo value.** Medium but disproportionately credible — a system that measures its own errors reads as mature. **Overclaiming risk.** Low, and it actively reduces overclaiming elsewhere.

### N-9 · Data Integrity Badge and degraded-mode transparency

**Why.** Every zone shows its data provenance — live CV, device-derived, simulated, or stale — and the system-wide header shows connectivity and confidence state. This is how we satisfy the no-fake-AI rule *visibly, in the product*, and it doubles as the honest answer to the network-outage constraint.

**Difficulty.** Low. **Demo value.** High, because it pre-empts the judge's sharpest question. **Overclaiming risk.** Low by construction.

### N-10 · Corroboration scoring for citizen reports

**Why.** Citizen reports are valuable signal and also an attack surface: one prankster should never be able to nudge an evacuation. Cluster reports in space and time, weight by independence and reporter history, and require multiple independent reports before a report materially moves the risk score.

**Solves.** "Incident reporting" (official) made safe to actually wire into the risk engine.

**Difficulty.** Low to medium. **Demo value.** Medium. **Overclaiming risk.** Low.

### Deferred but noted

Phone-as-sensor camera nodes (a spare Android on a monopod as a counting node — strong fit with "minimum hardware dependencies," worth building if time allows), and capacity-aware evacuation allocation via min-cost flow rather than nearest-exit routing (naive nearest-exit guidance is itself a crush mechanism; worth stating even if we implement the simpler version).

---

## 4. User Roles

Four roles. The fourth could be folded into the first; the reason not to is given below.

### R1 · Control Room Operator / Incident Commander

**Who.** Police or civil administration staff in a district or venue control room; in the brief's framing, the primary customer. Assume modest hardware, mixed technical confidence, high stress, and a strong preference for Hindi or a regional language alongside English.

**Sees.** Live venue map with heat overlay and risk zones; ranked alert queue; per-zone detail with trends, TTC, instability, and explainability card; ranked recommendations with intervention previews; field responder positions and task status; citizen report stream with corroboration; system health and confidence.

**Can do.** Acknowledge and adjudicate alerts; approve, modify, or reject recommendations; dispatch tasks to responders; author and approve public announcements from templates; open/close gates and set one-way flow *in the model* to reflect ground reality; trigger event-wide broadcasts; declare and clear incidents.

**Receives.** All severities from LOW upward, with escalating interruption. INFO is available but does not interrupt.

**Responsible for.** Every consequential decision. The system recommends; this role decides. No intervention, dispatch, or public broadcast is ever automatic.

### R2 · Field Responder / Ground Staff

**Who.** Security personnel, police constables, volunteers, marshals — on foot, on a phone, one hand free at best.

**Sees.** A short task list, their own position and assignment on a simplified map, the risk state of their immediate area, and nothing else. Deliberately minimal.

**Can do.** Accept and acknowledge tasks; mark en route, arrived, completed; report an outcome including "nothing found"; confirm physical state changes (gate opened, barricade moved); raise a report from the ground with photo and note; request backup.

**Receives.** Only tasks assigned to them, plus HIGH and CRITICAL alerts for their current zone.

**Responsible for.** Ground truth. This role is what makes the loop close — without it, "verification recommended" is a dead end and every anomaly stays unresolved. It is also the source of the labels that make N-8 possible.

### R3 · Citizen / Attendee

**Who.** Anyone at the event with the app. Assume low battery, poor connectivity, unfamiliarity with the venue, and multiple languages.

**Sees.** A simplified safety view of their surroundings — crowd conditions near them, recommended routes, gate status — in their chosen language. **Never the risk score, never the alert queue, never other people's anomalies.**

**Can do.** Submit an incident report with category, optional photo, and location; opt into Guardian Mode; clear their own Guardian prompt; set language; view safe-route guidance.

**Receives.** Location-scoped advisories from MODERATE, push notifications from HIGH, and instruction-bearing broadcasts at CRITICAL.

**Responsible for.** Their own movement decisions only.

**Design constraint.** Citizen messaging is action-framed, never threat-framed. "Gate 3 is very crowded — Gate 5 is 4 minutes away and clear" is safe. "Stampede risk detected at Gate 3" could produce the panic we are trying to prevent. This is a safety requirement, not a copywriting preference.

### R4 · Event Administrator / Configurator

**Who.** The person who sets up an event: venue map, zones, capacities, gates, thresholds, staff roster, languages, sensor registration.

**Sees.** Configuration surfaces and post-event analytics. Not the live operational surface.

**Can do.** Author the venue graph, set capacities and thresholds, register camera and simulation sources, manage users and roles, review after-action reports, apply threshold recalibrations proposed by N-8.

**Receives.** No live alerts.

**Responsible for.** The configuration that everything else derives from.

**Why this is separate from R1.** Threshold and capacity values *are* the safety envelope. Letting a stressed operator lower a threshold mid-incident to silence an alarm is a known failure pattern in safety systems, so authoring those values is separated from live operation. If we later merge them into one account, it should be as a distinct permission with an audit trail, not as an unremarked capability.

No analyst, medical, PR, or executive roles. After-action review folds into R4; everything else is a report, not a role.

---

## 5. Core User Journeys

### Journey A — Normal Crowd (baseline)

Attendees arrive; inflow is registered at gates. Each active source produces feature vectors every few seconds; the processing layer maintains per-zone density, mean speed, flow direction, coherence, and instability. Every zone stays within its normal band, so the risk engine holds all zones at INFO. The dashboard shows a green venue with live trend charts and a data integrity badge per zone. No alerts, no notifications, no tasks. The system writes a continuous baseline record, which matters: the per-zone "normal" profile learned during calm periods is what makes later anomaly detection meaningful. Citizen apps show ordinary conditions and route information.

**This journey must be demoed** — a system that only shows red is not credible.

### Journey B — Increasing Congestion

A context event occurs (gates open, a train arrives, a performance ends). Inflow to a zone rises. Density climbs and its growth rate crosses the watch band, so the zone moves to LOW: visible on the dashboard, no interruption. Over the next windows, mean speed begins falling while density continues rising — the laminar-to-jam signature — and instability begins climbing. Two independent signal families are now elevated, which satisfies the corroboration rule, and the zone escalates to MODERATE. TTC appears: critical threshold projected in roughly nine minutes, wide confidence band. The operator receives a non-modal alert with an explainability card showing the contributing signals and their exact contributions. The recommendation engine matches playbooks against the current condition, filters for feasibility, simulates each candidate, and returns a ranked list with projected effects — at this stage low-disruption options such as redirecting new inflow and increasing staff presence at the constriction. Citizens in the affected geofence receive an in-app advisory suggesting a less crowded route, without a push interruption.

### Journey C — Critical Crowd Risk

Conditions continue to deteriorate: density passes the crush band, mean speed is near zero, velocity variance is rising, the downstream gate is at capacity, and a corroborated citizen report arrives. A hazard override applies — high density with insufficient egress forces a minimum severity regardless of the weighted score — and the zone goes HIGH, then CRITICAL. The alert is modal and audible; unacknowledged, it escalates on a timer to the next contact. TTC now reads two to four minutes. Recommendations reprioritise toward high-impact actions, and critically, the ranking now accounts for **action lead time**: an intervention that takes six minutes to have effect is deprioritised when TTC is three. The operator selects a bundle — open an alternate exit, halt inflow at two gates, set a corridor one-way, deploy staff — reviews the intervention preview, and approves. Tasks dispatch to named responders; a multilingual announcement is generated from a pre-approved template, shown to the operator, edited if needed, and released only on approval. Responders acknowledge, execute, and confirm the physical changes, which update the venue graph. The system then monitors the outcome, tracking whether risk actually falls against the projection, and flags the intervention as ineffective if it does not.

### Journey D — Potentially Immobilized Person

A Guardian Mode user's device detects displacement and activity near zero over a sustained window while the surrounding zone's crowd is moving at normal speed. On-device confidence is computed from positional accuracy, neighbour sample count, and sensor availability; below threshold, nothing happens. Above threshold, the device prompts the user: "Are you okay?" with a countdown. A tap clears it and nothing is sent. **This is the primary false-positive filter and it costs the control room nothing.** If unanswered, a pseudonymous Check-On Request is created with zone-level location, anomaly duration, and confidence, and appears as a low-priority verification task — deliberately not as an incident. Multiple such anomalies clustered in one zone raise its priority and independently feed the zone's anomaly signal, because a cluster is a much stronger indicator than a single case. The nearest available responder is suggested; the operator dispatches. The responder verifies and resolves with an outcome: assisted, no issue found, false alarm, unable to locate. That outcome is recorded as a label and feeds N-8's precision reporting.

**What is never claimed:** that a person is injured, unconscious, or in danger. The output is an unverified anomaly and the product says so in those words.

### Journey E — Network Outage

Connectivity to the cloud is lost. Processing nodes continue computing features locally and queue outputs in a bounded local buffer with idempotent event IDs. A control-room local server continues running detection, risk scoring, and alerting for the sources it can still reach, so the operator retains a working — if narrower — picture. The dashboard switches to a visible DEGRADED state naming exactly what is unavailable, and confidence values fall automatically to reflect reduced input coverage, which in turn raises escalation thresholds slightly to avoid alarming on thin data. Mobile clients fall back to a cached risk map, cached geofences, and cached routes, and can raise local geofence warnings without connectivity; Guardian Mode continues detecting on-device and queues anomalies. Reports composed offline queue for later submission. Where configured, SMS and venue PA remain as out-of-band alert channels. On reconnection, queued events sync and are reconciled by event ID and timestamp with no duplication, and the timeline is backfilled so the after-action record is complete.

**What we do not claim:** that the system operates at full capability offline, or that mobile devices form a mesh network. Devices do not talk to each other; they degrade gracefully and resynchronise.

---

## 6. Functional Requirements

### Sensing and ingestion

- **FR-001** `[I]` The system shall ingest crowd feature vectors from registered processing sources at a configurable interval, with a default target to be set in §19.
- **FR-002** `[I]` The system shall accept video-derived input from at least one live or file-based camera source.
- **FR-003** `[I]` The system shall accept a simulated crowd data source that drives the full pipeline identically to a real source.
- **FR-004** `[N]` The system shall accept device-derived movement signals (speed, heading, positional accuracy) from consenting mobile clients.
- **FR-005** `[N]` Every ingested record shall carry source ID, source type, timestamp, and a quality indicator.
- **FR-006** `[N]` The system shall mark any source whose last update exceeds a staleness threshold as stale and exclude it from live scoring.
- **FR-007** `[I]` The system shall ingest gate and barricade state changes as operator- or responder-asserted events.
- **FR-008** `[I]` The system shall ingest scheduled context events (gate opening, ceremony times, transit arrivals, performance end) from event configuration.
- **FR-009** `[N]` Video-derived processing shall transmit only derived numeric features by default, never raw video frames or images of individuals.

### Monitoring and detection

- **FR-020** `[O]` The system shall estimate crowd density per zone and express it in persons per square metre and as occupancy against configured capacity.
- **FR-021** `[O]` The system shall estimate mean crowd movement speed per zone.
- **FR-022** `[O]` The system shall estimate dominant crowd flow direction per zone and per connection.
- **FR-023** `[N]` The system shall compute directional coherence (dispersion of movement headings) per zone.
- **FR-024** `[O]` The system shall identify and rank congestion hotspots across the venue.
- **FR-025** `[O]` The system shall identify bottlenecks, defined as connections where sustained inflow exceeds outflow capacity, and shall report the dominant cause.
- **FR-026** `[O]` The system shall detect reverse crowd movement, defined as sustained flow opposing the configured or established dominant direction.
- **FR-027** `[O]` The system shall detect counterflow, defined as significant simultaneous opposing flows within one zone or connection.
- **FR-028** `[O]` The system shall detect unusual crowd behaviour as statistically significant deviation from that zone's learned baseline profile for the comparable time window.
- **FR-029** `[N]` The system shall specifically detect a speed-collapse-under-rising-density pattern and report it as a distinct named condition.
- **FR-030** `[N]` The system shall compute a Crowd Instability Index per zone from density and velocity dispersion.
- **FR-031** `[N]` The system shall detect stop-and-go wave patterns in zones with sufficient temporal resolution, or explicitly report the condition as not assessable.
- **FR-032** `[O]` The system shall detect route blockage, defined as a connection whose throughput falls near zero while upstream density is significant.
- **FR-033** `[I]` The system shall detect sudden crowd surge as density growth rate exceeding a configured band over a short window.
- **FR-034** `[N]` The system shall maintain a per-zone rolling baseline profile of normal conditions for use by FR-028.

### Prediction

- **FR-040** `[O]` The system shall produce a short-horizon forecast of density per zone over a configurable horizon, with an uncertainty band.
- **FR-041** `[N]` The system shall compute a Time-To-Critical estimate per zone, expressed as a range with a confidence level, and shall return an explicit "not projected to reach critical" value where applicable.
- **FR-042** `[O]` The system shall identify zones projected to become high-risk before they reach that state, and shall distinguish these from zones already high-risk.
- **FR-043** `[O]` The system shall produce a crowd-crush risk indication per zone, derived from density, instability, and egress adequacy, presented as a risk level with contributing factors.
- **FR-044** `[O]` `[I]` The system shall present stampede likelihood as a bounded qualitative risk level with stated basis, and shall not present it as a calibrated probability.
- **FR-045** `[O]` `[N]` The system shall provide a panic-propagation projection over the venue graph, explicitly labelled as a simulation with visible assumptions.
- **FR-046** `[N]` Every predictive output shall carry a confidence value and the identity of the inputs it depended on.
- **FR-047** `[N]` The system shall record every prediction with its timestamp so that predicted versus actual outcomes can be compared after the event.

### Risk engine

- **FR-050** `[I]` The system shall compute a per-zone risk score on a 0–100 scale from a transparent weighted composition of normalised signal families.
- **FR-051** `[I]` The system shall assign each zone a severity level per §10.
- **FR-052** `[N]` The system shall expose the exact contribution of each signal to the resulting score.
- **FR-053** `[N]` The system shall apply configurable hazard override rules that force a minimum severity when specified conditions co-occur, independent of the weighted score.
- **FR-054** `[N]` The system shall require a condition to persist for a configurable number of consecutive evaluation windows before escalating severity.
- **FR-055** `[N]` The system shall apply hysteresis such that de-escalation thresholds are strictly lower than escalation thresholds.
- **FR-056** `[N]` The system shall require corroboration from at least two independent signal families before escalating to HIGH or above, except where a hazard override applies.
- **FR-057** `[N]` The system shall compute an input-quality confidence factor per zone and shall reflect it in both the displayed confidence and escalation behaviour.
- **FR-058** `[I]` All weights, thresholds, and override rules shall be externally configurable without code changes, and shall be versioned.
- **FR-059** `[N]` The system shall label all shipped default weights as uncalibrated engineering estimates in both the UI and documentation.

### Recommendation engine

- **FR-060** `[O]` The system shall generate recommended interventions drawn from a defined playbook library covering, at minimum, the eight intervention types listed in §2.5.
- **FR-061** `[N]` Each recommendation shall be generated only when its machine-checkable preconditions are satisfied by current state.
- **FR-062** `[N]` Each recommendation shall state the specific measured conditions that triggered it.
- **FR-063** `[N]` The system shall filter candidate recommendations for physical and resource feasibility against the venue graph and staff availability.
- **FR-064** `[N]` The system shall reject any candidate violating a safety invariant, including closing an exit while occupancy exceeds safe egress capacity, routing crowd into a higher-risk zone, or creating new counterflow.
- **FR-065** `[N]` The system shall rank recommendations by projected risk reduction relative to disruption cost, accounting for each action's lead time against the zone's Time-To-Critical.
- **FR-066** `[N]` The system shall provide an intervention preview projecting per-zone risk with and without the candidate action, labelled as simulation.
- **FR-067** `[O]` `[I]` The system shall compute a safest-route recommendation between a zone and an exit using risk-weighted path cost, not shortest distance alone.
- **FR-068** `[O]` `[I]` The system shall recommend security personnel redistribution as specific assignments to specific locations with stated justification.
- **FR-069** `[N]` The system shall record every recommendation together with the operator's disposition (approved, modified, rejected) and the observed outcome.

### Alerting

- **FR-070** `[I]` The system shall raise alerts on severity transitions, not on every evaluation window, and shall deduplicate alerts for a continuing condition.
- **FR-071** `[I]` Alerts shall be delivered to the dashboard in real time without page refresh.
- **FR-072** `[I]` The system shall require operator acknowledgement of HIGH and CRITICAL alerts.
- **FR-073** `[N]` The system shall escalate unacknowledged HIGH and CRITICAL alerts after a configurable interval.
- **FR-074** `[O]` The system shall deliver location-based warnings to citizen clients whose last known position falls within an affected zone's geofence.
- **FR-075** `[O]` The system shall deliver citizen-facing alerts in the recipient's selected language.
- **FR-076** `[N]` Citizen-facing alert content shall be action-framed and shall not contain threat language such as "stampede" or "crush."
- **FR-077** `[N]` No alert, dispatch, gate change, or public broadcast shall be issued automatically without operator approval.
- **FR-078** `[I]` De-escalation from HIGH or CRITICAL shall require both sustained improvement and explicit operator confirmation.
- **FR-079** `[N]` Where configured, the system shall support at least one out-of-band alert channel usable when data connectivity is unavailable.

### Command dashboard

- **FR-080** `[O]` The dashboard shall display a live event map of the venue with all zones and connections.
- **FR-081** `[O]` The dashboard shall display a crowd density heat map overlay on the venue map.
- **FR-082** `[O]` The dashboard shall display current risk zones with severity-coded treatment.
- **FR-083** `[O]` The dashboard shall display crowd trend analytics over a selectable time window, including density, speed, and risk.
- **FR-084** `[I]` The dashboard shall provide a severity-ordered alert queue with acknowledgement and adjudication controls.
- **FR-085** `[I]` The dashboard shall provide a per-zone detail view containing all current signals, trends, forecast, TTC, and explainability card.
- **FR-086** `[I]` The dashboard shall display ranked recommendations with previews and approval controls.
- **FR-087** `[I]` The dashboard shall display field responder positions, availability, and task status.
- **FR-088** `[I]` The dashboard shall display incoming citizen reports with corroboration state and location.
- **FR-089** `[N]` The dashboard shall display a data integrity badge per zone indicating provenance: live CV, device-derived, simulated, or stale.
- **FR-090** `[N]` The dashboard shall display a system-wide status banner covering connectivity, source health, and overall confidence.
- **FR-091** `[O]` `[I]` The dashboard shall provide an announcement composer using pre-approved templates with multilingual rendering and mandatory operator approval before release.
- **FR-092** `[I]` The dashboard shall provide a chronological event timeline for the active event.
- **FR-093** `[O]` `[I]` The dashboard shall be operable at a resolution and on hardware typical of a modest control room, and shall support a high-contrast presentation.
- **FR-094** `[O]` `[I]` The dashboard interface shall support at least English and one Indian language.

### Citizen mobile application

- **FR-100** `[O]` The app shall display crowd conditions for the user's current area in simplified, non-technical form.
- **FR-101** `[O]` The app shall deliver incident notifications relevant to the user's location.
- **FR-102** `[O]` The app shall deliver live congestion alerts in the user's selected language.
- **FR-103** `[O]` The app shall deliver location-based warnings via geofence evaluation.
- **FR-104** `[O]` The app shall allow submission of an incident report with category, free text, optional photo, and location.
- **FR-105** `[I]` The app shall support language selection covering at least three languages including English.
- **FR-106** `[O]` `[I]` The app shall display recommended safe routes and gate status for the user's position.
- **FR-107** `[N]` The app shall cache the latest risk map, geofences, and routes and shall remain functional in read-only form without connectivity.
- **FR-108** `[N]` The app shall queue reports composed offline and submit them on reconnection without duplication.
- **FR-109** `[N]` The app shall not display venue-wide risk scores, other users' data, or the operator alert queue.
- **FR-110** `[N]` The app shall obtain explicit, granular consent before collecting any location or motion data, and shall function in a reduced mode without such consent.
- **FR-111** `[N]` The app shall provide a visible indicator whenever it is contributing movement data.
- **FR-112** `[N]` The app shall allow the user to revoke consent and delete their contributed data at any time.

### Field responder application

- **FR-120** `[I]` The responder app shall display tasks assigned to the current user, ordered by priority.
- **FR-121** `[I]` The responder app shall support task state transitions: accepted, en route, arrived, completed.
- **FR-122** `[I]` The responder app shall require an outcome selection on task completion, including a "nothing found" option.
- **FR-123** `[I]` The responder app shall allow confirmation of physical state changes that update the venue graph.
- **FR-124** `[I]` The responder app shall allow ground reporting with photo and note.
- **FR-125** `[I]` The responder app shall display HIGH and CRITICAL alerts for the responder's current zone.
- **FR-126** `[N]` The responder app shall queue state transitions when offline and sync on reconnection.
- **FR-127** `[I]` The responder app shall support a backup request that appears in the operator queue.

### Guardian Mode (differential immobility anomaly)

- **FR-130** `[N]` Guardian Mode shall be strictly opt-in, disabled by default, with its purpose and limitations stated in plain language at the point of consent.
- **FR-131** `[N]` The device shall compute an immobility indication locally from displacement and motion-sensor activity over a configurable window.
- **FR-132** `[N]` The system shall compare individual movement state against the surrounding zone's crowd movement baseline over the same window.
- **FR-133** `[N]` The system shall compute anomaly confidence from positional accuracy, neighbour sample sufficiency, sensor availability, and data freshness, and shall suppress anomalies below a configured confidence floor.
- **FR-134** `[N]` On detection, the device shall prompt the user with a self-clearance option and a countdown before any report is transmitted.
- **FR-135** `[N]` An unresolved anomaly shall generate a Check-On Request containing zone-level location, duration, and confidence, and shall carry status `unverified`.
- **FR-136** `[N]` Check-On Requests shall be pseudonymous by default and shall not expose user identity to the control room unless the user has elected to share it or a responder has been dispatched.
- **FR-137** `[N]` No system output shall assert that a Guardian Mode subject is injured, unconscious, or in medical distress; all copy shall describe an unverified anomaly requiring verification.

### Resilience and offline behaviour

- **FR-140** `[O]` `[I]` Processing nodes shall continue computing features and shall buffer output locally when the backend is unreachable.
- **FR-141** `[O]` `[I]` The system shall support a control-room-local deployment capable of detection, risk scoring, and alerting without internet connectivity.
- **FR-142** `[N]` All events shall carry idempotent identifiers so that replayed buffered events do not duplicate.
- **FR-143** `[N]` On reconnection the system shall reconcile buffered events and backfill the timeline in correct chronological order.
- **FR-144** `[N]` The system shall display a degraded-mode indication naming precisely which capabilities are unavailable.
- **FR-145** `[N]` Reduced input coverage shall automatically lower reported confidence.
- **FR-146** `[N]` Local buffers shall be bounded, with a defined and documented eviction policy.
- **FR-147** `[N]` The system shall never present stale data as current; every displayed value shall carry an observation time.

### Privacy, security, audit

- **FR-150** `[O]` `[I]` The system shall not perform facial recognition, biometric identification, or persistent individual re-identification.
- **FR-151** `[O]` `[I]` Video processing shall retain only derived aggregate features by default; frame retention shall be off by default and, if enabled, time-limited and access-controlled.
- **FR-152** `[O]` `[I]` Device movement contributions shall be aggregated to zone level for crowd statistics, and individual traces shall not be reconstructible from stored crowd data.
- **FR-153** `[I]` The system shall enforce role-based access control across all four roles per §4.
- **FR-154** `[I]` The system shall maintain an append-only audit log of every operator action, approval, dispatch, broadcast, and configuration change, with actor and timestamp.
- **FR-155** `[I]` Configuration changes to weights, thresholds, and overrides shall be versioned and attributable.
- **FR-156** `[I]` The system shall apply documented retention limits per data category, with the shortest applied to individual-derived data.
- **FR-157** `[I]` All client-server communication shall be encrypted in transit.

### Learning and after-action

- **FR-160** `[N]` The system shall require adjudication of every alert as confirmed, false, or unclear before an event can be closed.
- **FR-161** `[N]` The system shall report per-event alert counts by severity and adjudication outcome.
- **FR-162** `[N]` The system shall compare recorded predictions against observed outcomes and report the result.
- **FR-163** `[N]` The system shall propose threshold adjustments based on adjudication history, for administrator review, and shall never apply them automatically.
- **FR-164** `[O]` `[N]` The system shall generate a natural-language incident summary derived solely from recorded event data, with source events traceable from the summary.
- **FR-165** `[N]` Generated summaries shall be labelled as machine-generated and shall be editable before export.
- **FR-166** `[I]` The system shall export an after-action report containing the timeline, alerts, adjudications, interventions, and outcomes.

### Advanced and bonus

- **FR-170** `[O]` `[N]` The system shall provide a venue model view showing zones, connections, capacities, and live state — the digital twin foundation.
- **FR-171** `[O]` `[N]` The system shall provide a crowd movement simulation over the venue graph, usable both for demo data generation and for intervention preview, always labelled as simulation.
- **FR-172** `[O]` `[N]` The system may provide a voice interface supporting a bounded set of read-only query intents.
- **FR-173** `[N]` The voice interface shall not execute state-changing commands without on-screen confirmation.
- **FR-174** `[O]` `[N]` The system may provide a multilingual assistant answering questions grounded strictly in current system state, and shall decline rather than speculate when data is absent.
- **FR-175** `[N]` No generative model output shall influence risk scores, severity levels, or recommendation selection.
- **FR-176** `[O]` `[N]` Announcement generation shall operate by filling slots in pre-approved templates and shall include a back-translation check surfaced to the operator for non-English output.

---

## 7. Non-Functional Requirements

Where there is no defensible basis for a number, this document says so. **"TBD-§19"** means the value is a design target to be decided with evidence.

**Latency.** The meaningful budget is end-to-end: sensor observation to visible operator alert. Given that the official lead-time ambition is ~10 minutes, sub-second pipeline latency is not the binding constraint — but operator *interaction* latency is, because a dashboard that lags feels untrustworthy under stress. Targets: map and alert updates perceptibly immediate on state change (TBD-§19, order of 1–2s); per-source feature computation faster than the ingestion interval so no backlog accumulates; dashboard interactions responsive to direct manipulation. Detection windows are inherently multi-second because instability and growth rate are defined over time — this is a property of the physics, not a performance defect, and we should say so rather than pretending to instantaneous detection.

**Scalability.** Design targets, to be validated rather than asserted: tens of zones per venue, tens of concurrent processing sources, and citizen clients in the thousands per event with room to grow. The architectural commitment that makes this plausible is that per-source bandwidth is *feature vectors, not video* — a few hundred bytes per source per interval — so ingest scales with zones rather than with pixels. Horizontal scale path: stateless ingest and API tier, partition by event, per-zone computation independent and parallelisable. Actual load ceilings: TBD-§19, measured.

**Availability.** The system must be useful in three distinct states, and this is more important than a nines figure we cannot back: fully connected (all capabilities); cloud-unreachable (control-room-local operation, reduced sources, degraded badge); client-offline (cached read-only mobile). No single-point failure should silence alerting for sources that remain reachable. Target uptime figures for a production deployment: TBD-§19.

**Privacy.** Non-negotiable positions: no facial recognition, no biometric identification, no persistent individual re-identification, and no raw video leaving the processing node by default. Device data is opt-in, granular, revocable, aggregated to zone level for crowd statistics, and short-retention. Guardian Mode is separately opt-in and pseudonymous by default. India's DPDP Act 2023 framing applies — purpose limitation, data minimisation, consent, and retention limits — and a real deployment involving government authorities and public-space monitoring needs actual legal review, which we should state rather than imply we have done.

**Security.** RBAC across the four roles; encryption in transit; append-only audit log for every consequential action; authenticated and registered processing sources so a rogue source cannot inject state; rate limiting and corroboration on citizen reports so report submission is not an attack vector; configuration changes attributable and versioned. Threat model to be written: TBD-§19.

**Explainability.** Every alert exposes its exact signal contributions; every recommendation states the measured conditions that triggered it; every prediction names its inputs; every displayed value carries an observation time and provenance. The design rule that makes this achievable is that the risk function is a transparent composition rather than a learned black box — explainability is an architectural property here, not a feature bolted on.

**Reliability and fault tolerance.** Graceful degradation over failure: a dead source is marked stale and excluded, not silently averaged in. Bounded buffers with documented eviction. Idempotent event handling so replay is safe. Watchdog on processing nodes. Persistence and hysteresis to prevent alert flapping. Explicit handling of the "insufficient data" case at every layer — the system must be able to say "I don't know," and this is a functional requirement of a safety tool, not a weakness.

**Usability.** The operating assumption is a stressed, non-specialist user in a police or civil control room. Consequences: the primary screen must convey venue state at a glance with no interaction; severity must be distinguishable by shape and text, not colour alone; the most urgent action must always be the most prominent element; no destructive or public-facing action without explicit confirmation; the number of concepts an operator must learn should be small and named in plain language. Field responder UX is one-handed, glanceable, and works on low-end Android.

**Accessibility.** Colour-blind-safe severity encoding with redundant shape and text cues; WCAG AA contrast as the target for both dashboard and app; adequate touch target sizes; text scaling; screen-reader labelling on critical controls; and for the citizen app specifically, comprehension by low-literacy users — which argues for icons and short imperative sentences over paragraphs, in every supported language.

**Cost.** The official constraint is low-cost with minimum hardware dependencies. Design commitments: zero mandatory new hardware (reuse existing CCTV; optionally a spare Android phone as a camera node); CPU-viable inference so no GPU is required per site, with GPU as an optional accelerator; feature-only transmission to minimise bandwidth cost, which matters on metered rural connections; open-source model weights and libraries to avoid per-inference licence costs; and generative AI confined to low-frequency, non-critical tasks — summaries, translations, assistant queries — so token cost scales with incidents rather than with monitoring time. Per-venue cost estimate: TBD-§19.

---

## 8. AI/ML Requirements

Specified per task. Several of these are *not* machine learning, and saying so is part of the point — a derived physical quantity is more reliable and more explainable than a model trained on data we do not have.

### AI-1 · Crowd density estimation

**Input.** Single video frame from a registered camera source, plus a homography or approximate ground-plane calibration for that view.

**Processing.** Density-map regression — the model outputs a per-pixel density map that integrates to a count.

**Output.** Estimated persons per zone and per grid cell, with an uncertainty indication.

**Model type.** A crowd-counting density-regression CNN of the CSRNet / MCNN family, or a point-based counting model such as P2PNet. **Explicitly not object detection.** Detection-based counting (YOLO and relatives) degrades badly in exactly the regime that matters: heavy occlusion, heads at small pixel scale, crowds of hundreds. Density regression was developed for this regime and is the right family. If detection is used at all it should be limited to sparse-crowd zones where it is genuinely more accurate.

**Training data.** Requires it, but does *not* require us to label any: pretrained weights on public crowd-counting benchmarks (ShanghaiTech, UCF-QNRF, JHU-CROWD++, NWPU-Crowd) are available and appropriate. Site-specific fine-tuning would improve accuracy and is a production concern.

**Simulation initially.** Yes — simulated sources can emit density values directly, bypassing the vision stage, so the whole downstream pipeline is testable without any camera.

**Confidence.** Derived from calibration quality, view geometry (oblique far-field views are much worse), lighting, and known domain shift from training data. Reported alongside every estimate.

**Failure modes.** Severe undercount at extreme density; sensitivity to camera angle and lens; night, rain, fog, and glare; domain shift from benchmark imagery to Indian venue conditions; non-person objects and vehicles; double-counting across overlapping views.

**Human verification.** Required at configuration time — an operator should sanity-check estimates against a known reference before an event, and the system should support a per-source correction factor.

### AI-2 · Crowd movement: speed, direction, coherence

**Input.** Consecutive frames from a camera source.

**Processing.** Dense optical flow producing a per-pixel motion field, aggregated to grid cells and zones for mean speed, dominant heading, angular dispersion, and velocity variance. Scale conversion via the same ground-plane calibration.

**Output.** Velocity field per zone; mean speed in m/s; dominant direction; circular variance of headings; velocity dispersion.

**Model type.** **Classical dense optical flow (Farnebäck) as the baseline; a learned flow model (RAFT) only where a GPU is available.** This is the most consequential model choice in the specification and it deserves justification: optical flow gives us the velocity *field* directly, which is precisely what the risk core needs, while requiring **no training data at all**, running on CPU, and never needing to solve the much harder problem of detecting or tracking individuals. Individual tracking in dense crowds is fragile, expensive, and privacy-hostile — and unnecessary, because we need aggregate fields, not identities.

**Training data.** None for the classical path. This is a major practical advantage.

**Simulation initially.** Yes — simulated sources emit velocity statistics directly.

**Confidence.** Degraded by low frame rate, motion blur, camera shake, low light, and low-texture scenes.

**Failure modes.** Camera motion misread as crowd motion (needs stabilisation or a static-camera assumption); the aperture problem in uniform regions; flow saturation at very high density where individual motion is small; illumination change misread as motion.

**Human verification.** Not per-frame. Verification at calibration time that speeds are physically plausible.

### AI-3 · Crowd Instability Index (crowd pressure proxy)

**Input.** Outputs of AI-1 and AI-2 over a rolling window.

**Processing.** **Deterministic computation, not machine learning.** Combine local density with velocity dispersion, following the structure of the crowd-pressure quantity used in crowd-disaster analysis, and track its trajectory alongside mean speed to identify the laminar → stop-and-go → turbulent progression.

**Output.** Instability value per zone; a named flow-regime label; the presence or absence of a speed-collapse pattern.

**Model type.** None. A formula with documented, configurable breakpoints.

**Training data.** None. Threshold calibration would benefit from real data and we do not have it — thresholds ship as uncalibrated defaults.

**Confidence.** Inherits from AI-1 and AI-2, degraded by short observation windows.

**Failure modes.** Thresholds not validated for Indian venue conditions or crowd composition; sensitivity to grid cell size; the underlying literature is derived from specific incidents and generalisation is an assumption, not a fact.

**Human verification.** The index informs severity; severity always presents to a human before action.

### AI-4 · Bottleneck and route-blockage detection

**Input.** Velocity field, zone densities, venue graph with configured capacities.

**Processing.** **Deterministic flow analysis, not ML.** Compute throughput per connection, compare against configured capacity, compute upstream queue growth from flow imbalance, classify the cause.

**Output.** Ranked bottlenecks with severity, queue growth rate, and cause; blockage detection where throughput approaches zero under upstream load.

**Model type.** None. Flow conservation on a graph.

**Training data.** None. Requires accurate configured capacities, which are a configuration-quality problem rather than a data problem.

**Failure modes.** Wrong configured capacity produces wrong conclusions; unobserved connections cannot be assessed and must be reported as unknown rather than as fine.

**Human verification.** Capacity configuration must be reviewed by someone who knows the venue.

### AI-5 · Unusual crowd behaviour detection

**Input.** Per-zone feature vector time series (density, speed, coherence, instability, flow balance).

**Processing.** Two complementary paths. **Unsupervised anomaly detection** against a per-zone learned baseline — Mahalanobis distance on the feature vector, or an isolation forest, or an autoencoder reconstruction error if data volume supports it — reported as deviation from that zone's normal profile for the comparable time window. Plus **explicit pattern detectors** for specific known-dangerous signatures: radial dispersal from a point (the panic signature), sustained counterflow, and abrupt coherent direction reversal.

**Output.** Anomaly score with the deviating features named; specific pattern flags when matched.

**Model type.** Unsupervised, plus deterministic pattern rules. **Deliberately not a supervised "abnormal behaviour classifier"** — that requires labelled abnormal-behaviour data which does not exist for this setting, and building one would mean fabricating labels.

**Training data.** No labels needed. Requires a baseline period of normal operation per zone, which is itself a limitation: a brand-new venue has no baseline, and early-event detection is therefore weaker.

**Simulation initially.** Partially. Simulation can generate both normal baselines and injected anomalies, which is useful for testing, but a simulated baseline does not prove the detector works on real crowds and we must not claim it does.

**Confidence.** Scales with baseline maturity and sample count.

**Failure modes.** Legitimate unusual-but-safe behaviour flagged (a performance ending, a mass prayer, a rain shower); slow drift absorbed into the baseline; the cold-start problem above.

**Human verification.** Always. Anomaly detection output is a prompt to look, never a conclusion.

### AI-6 · Short-horizon forecasting

**Input.** Per-zone scalar time series over a rolling window, plus scheduled context events.

**Processing.** Forecast density and inflow over a short horizon; derive Time-To-Critical from the projected trajectory against the zone's critical threshold.

**Output.** Forecast with uncertainty band; TTC as a range with confidence, or an explicit "not projected to reach critical."

**Model type.** **Start with transparent statistical methods** — exponentially weighted trend extrapolation with an uncertainty band derived from recent residuals, optionally a gradient-boosted regressor on lag features once real series exist. **Not an LSTM or transformer initially**, for a specific reason: a deep sequence model trained on a handful of simulated events would produce confident-looking output with no basis, which is exactly the fake-AI failure we are avoiding. A simple extrapolation with an honest error band is both more defensible and, at these horizons and data volumes, likely no worse. Sequence models become appropriate once there is real multi-event historical data.

**Training data.** Minimal for the baseline method; substantial for the learned alternatives.

**Simulation initially.** Yes for development, but forecast *accuracy* measured on simulated data must never be quoted as a performance claim.

**Confidence.** From recent residual variance; wide bands are the honest output early in an event.

**Failure modes.** Trend extrapolation cannot anticipate discontinuities — a sudden gate opening or an unscheduled surge breaks it, which is precisely why scheduled context events are an input and why AI-4's capacity reasoning matters as an independent path to the same conclusion.

**Human verification.** TTC is decision support; the operator decides.

### AI-7 · Panic propagation projection

**Input.** Venue graph, current zone states, an assumed origin.

**Processing.** Propagation over the zone adjacency graph — a compartmental or cellular-automaton spread model parameterised by connection capacity, density, and distance.

**Output.** A projected spatial and temporal spread pattern, labelled as simulation with assumptions displayed.

**Model type.** Rule-based simulation. **Not a trained predictive model** — no data exists to train one, and none can honestly be manufactured.

**Training data.** None; parameters are assumptions.

**Confidence.** Explicitly not a calibrated forecast. This must be presented as a planning and what-if tool.

**Failure modes.** Human panic behaviour is not well captured by simple propagation models; parameters are unvalidated.

**Human verification.** Framed as an exploratory aid throughout. **This is the single easiest capability in the whole specification to overclaim, and the wording in the UI matters as much as the code.**

### AI-8 · Differential Immobility Anomaly

Fully specified in N-6 and FR-130..137. In model terms: on-device threshold logic over displacement and motion-sensor activity, compared against a robust zone movement baseline (median and dispersion, robust to outliers), with confidence gating. **No ML model, deliberately** — a learned fall-detection model would need labelled fall data from crowd conditions that we do not have, and would invite exactly the medical-claim overreach we have ruled out.

Failure modes: GPS multipath and indoor drift; phone stationary while person is not; person stationary and fine; **and the structural blind spot that in a genuine crush the differential disappears because everyone stops.** Human verification is mandatory by design — the output *is* a verification request.

### AI-9 · Generative AI: summaries, translation, assistant

**Input.** For summaries: the structured event log only. For announcements: a pre-approved template plus slot values from system state. For the assistant: a user question plus retrieved current system state.

**Processing.** An LLM constrained to the supplied structured context.

**Output.** Incident summary with traceable source events; announcement text in target languages; grounded answers to bounded queries.

**Model type.** A general-purpose LLM via API, or a small local model where connectivity or cost demands it.

**Training data.** None of ours. No fine-tuning proposed.

**Confidence.** Not applicable in the risk sense, which is exactly the reason for the architectural rule: **no generative output may influence risk scores, severity, or recommendation selection** (FR-175). The LLM renders decisions; it does not make them. Announcements fill approved templates rather than authoring safety instructions freely, with a back-translation check surfaced to the operator, because a mistranslated evacuation instruction is a safety hazard.

**Failure modes.** Fabrication if context is thin; mistranslation, especially of imperatives and place names; tone drift into alarming language; latency and dependence on connectivity.

**Human verification.** Mandatory for anything published to the public. Summaries are labelled machine-generated and are editable before export.

---

## 9. Risk Model

The goal is a scoring architecture that is transparent, auditable, and calibratable — explicitly *not* a set of weights presented as scientifically validated.

### Signal families

Seven, each normalised to 0–1 by documented transfer functions.

**D — Density.** Persons per square metre; occupancy against configured capacity; pedestrian level-of-service band. Density is a necessary but insufficient signal, and its normalisation curve should be steeply non-linear — the difference between 2 and 3 persons/m² matters far less than between 5 and 6.

**G — Growth.** Rate of change of density; inflow-minus-outflow imbalance; surge detection over a short window. Growth is what converts a snapshot into a prediction, and it is the family that most directly serves the ten-minute ambition.

**P — Pressure and turbulence.** The Crowd Instability Index; the speed-collapse-under-rising-density pattern; stop-and-go wave presence; velocity dispersion. **This family should carry substantial weight, because it is the one most associated with crush onset rather than mere crowding.**

**F — Flow integrity.** Directional coherence; counterflow fraction; reverse movement; abrupt direction reversal.

**B — Structure and egress.** Bottleneck severity on connected edges; gate and exit capacity utilisation; blocked or closed exit state; **egress adequacy — occupancy against available exit capacity**, which is the signal that distinguishes a merely crowded space from a trap.

**A — Anomaly and behaviour.** Unsupervised deviation score; radial dispersal pattern; count of clustered immobility anomalies; corroborated citizen report count.

**C — Context.** Zone criticality (enclosed, stairs, single-exit, known historical choke point); proximity to a scheduled event moment; time since event start; weather where it affects surface conditions or visibility; prior incident history at this zone. Context does not create risk on its own — it modulates how much a given physical state should worry us.

### Composition

1. Normalise every signal to 0–1 by documented, configurable transfer functions with explicit breakpoints. Where pedestrian level-of-service bands from published pedestrian-planning literature are applicable, use them as the starting breakpoints and cite them as the source; elsewhere, breakpoints are venue configuration.
2. Reduce each family to a family score. **Use maximum rather than mean for the hazard families (B and A)** — one blocked exit must not be averaged away by three healthy ones — and weighted mean for the continuous families (D, G, P, F).
3. Base risk = weighted sum of family scores, scaled to 0–100.
4. Apply the context modifier from family C as a bounded multiplier rather than an additive term, so context amplifies real physical signal but cannot manufacture risk from nothing.
5. Apply **hazard overrides**: documented condition sets that force a minimum severity regardless of the weighted total. For example, density above the crush band combined with egress capacity below occupancy forces CRITICAL. This is the safety-interlock pattern from real engineered systems, and it exists because any weighted average can dilute a lethal single condition.
6. Apply **persistence and hysteresis** before any severity transition (FR-054, FR-055).
7. Compute **confidence** separately from risk, from input coverage, freshness, and source quality — and never fold confidence into the score itself, because "high risk, low confidence" and "moderate risk, high confidence" demand different operator responses and must remain distinguishable.

### Output contract

Risk score 0–100; severity band; confidence 0–1; ranked exact signal contributions; active override rules if any; Time-To-Critical range; and the identity of every input used.

### On weights — stated plainly

This document does not invent validated weights. What it commits to is this: initial weights are engineering judgment, informed by the general finding in crowd-safety literature that flow instability and egress adequacy are more predictive of crush than raw density, and they ship labelled as uncalibrated. The architecture's value is that weights, breakpoints, and overrides live in versioned configuration; that every score decomposes exactly into its contributions; and that adjudication data (FR-160..163) provides the mechanism by which weights could be calibrated against real outcomes.

**A real deployment would require calibration on venue data plus review by crowd-safety practitioners, and we should say that in the documentation, in the UI, and in the demo.** That honesty is a stronger position than a fabricated accuracy figure.

---

## 10. Alert Severity Model

Five levels, structured as **one informational tier plus four actionable tiers**. Reasoning: fewer than four actionable levels collapses the crucial distinction between "watch this" and "act now," which is the whole value of an early-warning system; more than five causes operators to miscalibrate under stress and is a known failure pattern in alarm design. Separating INFO out as explicitly non-interrupting protects the actionable ladder from noise.

### INFO (Level 0) — Awareness

- **Trigger concept.** Notable but normal state changes, and system events: source connected or lost, context event started, zone entering an elevated-but-normal band.
- **Visual.** Neutral grey; timeline entry; no map emphasis.
- **Notification.** None. Log only. Does not enter the alert queue.
- **Authority action.** None required.
- **Escalation.** None.

### LOW (Level 1) — Watch

- **Trigger.** A single signal family elevated with persistence satisfied, no corroboration; or a low-confidence higher-severity condition held down by the confidence gate.
- **Visual.** Blue with a distinct shape marker; zone outlined on map; queue entry at bottom.
- **Notification.** Dashboard only, no sound, no push. No citizen notification.
- **Authority action.** Awareness. Optionally increase observation of that zone.
- **Escalation.** Automatic to MODERATE if a second family elevates or the condition persists beyond a configured duration.

### MODERATE (Level 2) — Elevated

- **Trigger.** Two or more signal families elevated with persistence satisfied; or growth rate indicating a trajectory toward critical with TTC inside the horizon at usable confidence.
- **Visual.** Amber; zone shaded; queue entry raised; TTC displayed; explainability card available.
- **Notification.** Dashboard alert with soft audible cue. Field responders in the zone informed. **Citizens in the geofence receive an in-app advisory only — no push interruption.**
- **Authority action.** Review recommendations; consider low-disruption preventive interventions (redirect new inflow, staff presence at the constriction). This tier is where the system earns its lead time — MODERATE is the intended point of action, not HIGH.
- **Escalation.** Automatic to HIGH on continued deterioration or TTC falling below a configured threshold.

### HIGH (Level 3) — Danger developing

- **Trigger.** Pressure and structural families both strongly elevated, or TTC short with good confidence, or a hazard override at HIGH level.
- **Visual.** Red with strong shape and text encoding; zone prominently marked; alert pinned to top; recommendations surfaced without navigation.
- **Notification.** Persistent dashboard alert with sustained audible cue, requiring acknowledgement. Push to responders in and adjacent to the zone. **Push notification to citizens in the geofence, action-framed** ("Gate 3 is very crowded. Use Gate 5, 4 minutes away"). Out-of-band channel used where configured.
- **Authority action.** Act. Approve an intervention or explicitly record a decision not to. Dispatch staff.
- **Escalation.** Escalates to the next contact if unacknowledged within a configured interval; escalates to CRITICAL on continued deterioration.

### CRITICAL (Level 4) — Imminent or occurring

- **Trigger.** Crush-band conditions with inadequate egress; instability at turbulent levels; a confirmed incident; or any CRITICAL hazard override.
- **Visual.** Full-width modal treatment that cannot be missed, with the recommended action as the most prominent element on screen.
- **Notification.** All channels: dashboard modal and continuous audible, push to all responders, citizen broadcast with clear instructions in all supported languages, out-of-band channels, and venue PA where integrated.
- **Authority action.** Execute emergency intervention; consider declaring an incident; consider evacuation using safest-route output.
- **Escalation.** Immediate escalation to all configured contacts. **De-escalation requires both sustained measured improvement and explicit operator confirmation — never silent auto-clear** (FR-078).

### Cross-cutting rules

Severity is per zone; the venue-level indicator is the maximum across zones with a count at each level. Confidence gates escalation: a HIGH-scoring condition on thin data presents as LOW-with-uncertainty and a prompt to verify, rather than as HIGH — because a false CRITICAL is not a harmless error, it burns the operator's trust and the next real alert pays for it. Severity is always encoded redundantly in colour, shape, and text. No severity level ever triggers a public broadcast without operator approval.

---

## 11. Recommendation Engine

The requirement is "actionable interventions to pacify the situation." The failure mode to avoid is an LLM producing plausible-sounding advice. Our approach is a deterministic playbook engine with simulation-based ranking, where generative AI only phrases the result.

### Playbook structure

Each entry in the library is a structured object, not a prompt: an action type; machine-checkable preconditions over the signal vector and venue graph; required resources (staff, physical access, authority); a disruption cost; a lead time to effect; an expected mechanism of effect expressed as a change to the flow model; and safety invariants it must not violate. The library covers the eight official intervention types — open alternate exit, close entry gate, redirect incoming visitors, deploy staff, broadcast multilingual announcement, change barricade configuration, institute one-way flow, plus investigate/verify anomaly as the ninth, from N-6.

### Pipeline

1. **Match.** Evaluate all playbook preconditions against current state. Only satisfied playbooks become candidates, which is what ties every recommendation to measured conditions.
2. **Filter for feasibility.** Drop candidates the venue graph or roster cannot support — an unstaffed or locked gate cannot be opened; staff cannot be redeployed from a zone that would then fall below minimum cover.
3. **Check safety invariants.** Reject any candidate that would close an exit while occupancy exceeds safe egress capacity, route crowd into a zone at higher risk, create new counterflow in a constrained corridor, or reduce total egress capacity while density is rising. **These are hard rejections, and they are the reason a recommendation engine is safer than an LLM here** — an invariant is checkable; a plausible sentence is not.
4. **Simulate.** Run each surviving candidate through the flow model on the venue graph and project per-zone risk at T+5 and T+10 against a do-nothing baseline. Output: expected risk reduction, and any risk *increase* induced elsewhere, because redirecting a crowd moves the problem and the operator must see where.
5. **Rank.** Score by projected risk reduction relative to disruption cost, then apply a lead-time feasibility gate: an action whose lead time exceeds the zone's Time-To-Critical is demoted with the reason stated, because recommending a six-minute action three minutes from critical is worse than useless.
6. **Explain.** Present each recommendation with the triggering conditions in measured terms, the projected effect with its assumptions, the required resources, and the expected time to effect. The template is concrete: *"Open Exit 5 and halt inflow at Gates 2 and 3. Because: Zone D density 4.6/m² rising 0.4/m²/min; Corridor 2 outflow at 97% capacity; Exit 5 utilisation 31%. Projected: Zone D risk 78 → 41 by T+8; Zone F risk 22 → 34. Requires 3 staff at Exit 5. Effect begins ~2 min after execution."*
7. **Decide.** The operator approves, modifies, or rejects. Nothing executes automatically.
8. **Dispatch and track.** Approved actions become responder tasks. Confirmations update the venue graph.
9. **Verify outcome.** Compare actual risk trajectory against projection; flag interventions that are not producing the expected effect, so an operator is not left waiting on a plan that is not working. Record everything for after-action analysis.

### Where generative AI is allowed

Rendering the already-selected recommendation into fluent language for the operator; filling pre-approved announcement templates with slot values and rendering them in target languages with a back-translation check; and answering grounded operator questions about current state. It never selects, ranks, or filters an action. That boundary is architectural (FR-175).

---

## 12. Data Sources

### Required for prototype

| Source | Purpose | Privacy implications |
|---|---|---|
| Venue configuration (zones, connections, areas, capacities, criticality, gates, exits) | Foundation for the venue graph, bottleneck detection, routing, simulation | None. Static, non-personal. |
| Simulated crowd data generator | Drives the full pipeline for reliable demonstration and testing; generates baselines and injected scenarios | None. Must be visibly labelled as simulated. |
| Recorded or live video from at least one camera source (public crowd footage or a webcam) | Proves density and flow estimation are real, not scripted | Highest-sensitivity source. Mitigations: derived features only, no frame retention by default, no recognition or re-identification, and for public footage, use openly licensed material. |
| Operator and responder actions (acknowledgements, approvals, dispatches, confirmations, adjudications) | Closes the loop; produces labels for the learning layer | Staff activity data. Needs RBAC, audit logging, and staff awareness that actions are logged. |
| Citizen incident reports | Official requirement; corroborating signal | User-generated, potentially identifying via photos. Mitigations: optional photo, pseudonymous submission, no automatic face processing, retention limits, corroboration scoring to blunt malicious use. |
| Scheduled event context (gate opening times, ceremony schedule, session end) | Anticipates surges that trend extrapolation alone cannot see | None. |

### Useful but optional for prototype

| Source | Purpose | Privacy implications |
|---|---|---|
| Consenting mobile device movement signals | Novel movement signal in zones without camera coverage; enables Guardian Mode | Significant. Opt-in and granular consent, on-device processing, zone-level aggregation, no reconstructible individual traces, revocable, short retention. Guardian Mode separately consented and pseudonymous. |
| Additional camera sources, including a spare Android phone as a camera node | Wider coverage; demonstrates the low-hardware claim concretely | As above. |
| Weather data | Surface conditions and visibility affect crowd behaviour and evacuation viability | None. Only include if it actually feeds a signal — otherwise it is decoration. |
| Historical event records from prior runs of the same event | Better baselines, better thresholds, richer after-action comparison | Aggregate only. |

### Future production integrations

| Source | Purpose | Privacy implications |
|---|---|---|
| Existing venue CCTV via RTSP/ONVIF at scale | The realistic production sensing path — reuses installed infrastructure, no new hardware | Requires DPIA, signage, lawful basis, and operator agreements. |
| Ticketing, turnstile, and access-control counts | Ground-truth occupancy that dramatically improves density calibration | Personal data in the source system; ingest aggregate counts only. |
| Telecom or Wi-Fi presence analytics | Coverage-wide crowd estimation without cameras | High sensitivity and regulatory complexity. Aggregate-only, and only with a lawful basis. |
| Public transport arrival feeds | Anticipates external inflow surges before they reach the venue | Minimal. |
| Emergency services and medical dispatch integration | Closes the loop to actual response | Interagency data-sharing agreements needed. |
| Venue PA and digital signage control | Executes announcement recommendations directly | Requires strict authorisation controls. |
| SMS or cell broadcast for mass alerting | Reaches non-app users; works when data is down | In India requires DLT registration and operator agreements — a procurement timeline, not a coding task. |
| Social media monitoring | Corroborating signal | Noisy, low signal-to-effort, and an easy overclaim trap. Deliberately deferred. |

### Two cross-cutting positions

**Features, not video.** The single design decision that transmits *derived features rather than video* simultaneously satisfies privacy, bandwidth cost, and the network-outage constraint. That convergence is worth stating explicitly because it is genuinely elegant rather than a compromise.

**Phone-derived counts are penetration-biased.** If a fraction of the crowd has the app, you observe that fraction. We must never report absolute density from device data alone. What device data *can* honestly provide is relative change and movement statistics — which happen to be the more predictive signals — plus, where camera coverage overlaps, a measurable sampling ratio that can be used to extrapolate to uncovered zones with a stated and visible uncertainty. That approach is defensible. Claiming a headcount from phones is not.

---

## 13. System Architecture — Conceptual

```
Data Sources
    ↓
Data Ingestion
    ↓
Processing
    ↓
Detection
    ↓
Prediction
    ↓
Risk Engine
    ↓
Recommendation Engine
    ↓
Real-Time Event Layer
    ↓
Authority Dashboard / Mobile Users
    ↓
Incident Feedback
    ↓
Analytics / Learning
```

**Data Sources.** Cameras (existing CCTV, webcam, or phone-as-node), the simulation generator, consenting mobile devices, operator and responder inputs, citizen reports, venue configuration, and scheduled context. Every source is registered, authenticated, and typed, so provenance is known for every value in the system.

**Data Ingestion.** Normalises heterogeneous inputs into a single timestamped feature-vector schema, stamping source ID, source type, observation time, and quality. Validates and rejects malformed or unauthenticated input. Buffers locally when downstream is unreachable, with idempotent event IDs so replay is safe. **The critical design property: this layer receives features, not video.** Vision computation happens at the source node, which is what makes the bandwidth, cost, and privacy story work.

**Processing.** Turns raw features into the derived quantities the rest of the system reasons about: density per zone and cell, mean speed, dominant direction, coherence, velocity dispersion, flow rates per connection, and the Crowd Instability Index. Maintains rolling windows and per-zone baseline profiles. Marks stale sources and excludes them rather than silently averaging them in.

**Detection.** Evaluates the present state against thresholds, baselines, and physical definitions: hotspots, bottlenecks with cause, blockage, counterflow, reverse movement, surge, speed-collapse, unsupervised anomalies, and clustered immobility anomalies. Output is a set of typed, timestamped detections with confidence — facts about now.

**Prediction.** Extends the present forward: short-horizon density and inflow forecasts with uncertainty bands, Time-To-Critical per zone, identification of zones projected to become high-risk, and the labelled panic-propagation projection. Every prediction is persisted so it can later be checked against what happened.

**Risk Engine.** Composes detections, predictions, and context into a per-zone risk score, severity, and confidence, applying hazard overrides, persistence, hysteresis, and corroboration rules per §9. Emits the exact contribution decomposition. **This layer is deterministic and auditable by design** — it is the safety-critical core, and no learned or generative component sits inside it.

**Recommendation Engine.** Matches playbooks, filters for feasibility, enforces safety invariants, simulates candidates against the venue graph, ranks by projected benefit relative to cost and lead time, and attaches explanations. Produces candidates for human decision, never commands.

**Real-Time Event Layer.** Distributes state changes, alerts, recommendations, and task updates to connected clients with low latency, scoped by role and — for citizens — by geofence, so nobody receives data their role should not see. Handles reconnection and backfill.

**Authority Dashboard / Mobile Clients.** The three human surfaces: control-room dashboard (full picture, decisions), responder app (tasks, ground truth), citizen app (localised, simplified, multilingual, action-framed). Each is a deliberately different view of the same state.

**Incident Feedback.** Captures what humans did and what they found: acknowledgements, approvals, rejections, dispatches, responder outcomes including "nothing found," incident declarations, and alert adjudications. This layer is what makes the loop a loop rather than a one-way pipe — without it, "verification recommended" has no terminus and the system can never learn.

**Analytics / Learning.** Compares predictions against outcomes, computes and reports the system's own alert precision by severity, proposes threshold and weight recalibrations for administrator review (never auto-applied), generates the traceable incident summary, and exports the after-action report.

**Cross-cutting.** A venue model and configuration store, versioned and attributable, that the graph-dependent layers all read. An append-only event and audit store that is the single source of truth for the timeline. An identity and RBAC service. And an offline and sync subsystem spanning ingestion, clients, and the event layer, since resilience cannot be a single box in a diagram — it is a property of every layer that holds state.

---

## 14. Prototype vs Production

| Capability | Hackathon Prototype | Production Version |
|---|---|---|
| Crowd density estimation | Pretrained density-regression model on recorded crowd footage plus one live webcam feed, approximate manual ground-plane calibration, in one or two zones; remaining zones fed by the simulator and labelled as such | Site-calibrated models per camera, fine-tuned on venue imagery, validated against turnstile ground truth, across all covered zones with overlap deduplication |
| Movement, speed, direction | Real dense optical flow on the live camera zones; simulated velocity statistics elsewhere, labelled | Optical flow across all camera zones with stabilisation, night and weather handling, per-camera scale calibration |
| Crowd Instability Index | Real computation on real fields in the CV zones; thresholds are uncalibrated defaults, stated as such on screen | Thresholds calibrated on venue data and reviewed by crowd-safety practitioners; validated against incident history |
| Bottleneck detection | Real flow-conservation computation over a hand-authored venue graph with estimated capacities | Capacities derived from survey and measured throughput; automated calibration from observed flow ceilings |
| Unusual behaviour detection | Unsupervised detector against baselines built during the demo run plus explicit pattern detectors; short baseline period acknowledged as a limitation | Baselines accumulated over many events and comparable time windows; drift management; per-zone tuning |
| Forecasting and Time-To-Critical | Transparent trend extrapolation with visible uncertainty bands, driven by simulated and live series | Same method plus learned models trained on real multi-event history; accuracy measured and published internally |
| Stampede likelihood | Qualitative risk level with contributing factors and explicit statement that it is not a calibrated probability | Still not a calibrated probability without validation data; would require multi-venue longitudinal study and expert review before any probabilistic claim |
| Panic propagation | Rule-based propagation over the venue graph, on-screen "SIMULATION — assumptions shown" label | Parameterised from crowd-dynamics research and validated where ethically possible; remains a planning tool |
| Immobility anomaly (Guardian Mode) | Real detection on one or two demo phones, real comparison against zone baseline, full staged escalation and responder verification flow | Battery-optimised background operation across device classes, indoor positioning improvements, formal consent and DPIA, measured false-positive rate published to operators |
| Recommendation engine | Real playbook matching, feasibility filtering, safety invariants, and simulated projections over the venue graph | Larger playbook library co-authored with police and event-safety practitioners; effectiveness measured across events and fed back into ranking |
| Intervention preview | Real simulation on the venue graph under simple flow assumptions, clearly labelled | Higher-fidelity crowd simulation validated against observed venue behaviour |
| Command dashboard | Fully functional web dashboard: live map, heat map, risk zones, trends, alert queue, recommendations, explainability, responder and report views, integrity badges | Same, hardened: multi-event, multi-venue, role-scoped, tested under sustained load, accessibility-audited, localised |
| Citizen mobile app | Functional app or responsive PWA on real devices: localised alerts, geofenced warnings, reporting, cached offline mode, Guardian Mode opt-in | Native app, app-store distributed, push at scale, battery-optimised, accessibility-audited, more languages |
| Responder app | Functional task list, state transitions, outcome capture on a real device | Same, plus integration with existing police and event communications, and offline-first hardening |
| Multilingual announcements | Pre-approved templates with LLM slot-filling and rendering into three languages, back-translation shown, operator approval required | Professionally reviewed template library per language, PA and signage integration, verified translations |
| Alerting channels | In-app and dashboard alerting real; SMS and PA shown as mocked channel with the exact payload displayed and clearly identified as mocked | SMS via DLT-registered route, cell broadcast where available, venue PA and signage integration |
| Network outage handling | Live demonstrated: disconnect cloud, show local operation, degraded badge, confidence drop, cached mobile view, then reconnect and show clean sync with no duplicates | Same architecture, plus tested failure matrix, defined recovery objectives, and on-site redundancy |
| Scalability | One venue, roughly eight to twelve zones, a handful of sources, demo-scale clients; architecture explained and load ceilings stated as unmeasured | Multi-venue, load-tested, horizontally scaled, measured ceilings published |
| Learning loop | Real adjudication, real self-reported precision for the demo event, proposed threshold changes shown for review | Cross-event calibration, statistical validation, governed change-control on safety thresholds |
| Privacy posture | Architecturally enforced: features-only transmission, no recognition, opt-in device data, on-device Guardian processing, retention limits implemented | Same, plus DPIA, legal review under DPDP Act 2023, signage, published policy, third-party audit |

**The rule we hold to throughout the demo:** anything simulated is labelled simulated *on screen* at the moment it is shown, and anything not implemented is described as not implemented. The integrity badge (N-9) exists precisely so that this honesty is structural rather than dependent on the presenter remembering to say it.

---

## 15. What We Should NOT Build

**Facial recognition or any biometric identification.** Adds nothing to crush prediction — the risk core needs aggregate fields, not identities — while creating serious legal exposure under DPDP Act 2023 and a reputational liability with judges who will ask about it. It is also the single fastest way to make a public-safety tool politically unusable. Hard no.

**Individual person tracking or cross-camera re-identification.** Expensive, fragile in dense crowds, privacy-hostile, and unnecessary given that optical flow provides the velocity fields we actually need. Skipping it makes the system both better and cheaper.

**A custom-trained stampede classifier.** No labelled stampede-precursor data exists for these venues. Training one would mean fabricating labels and reporting a meaningless accuracy figure. This is the central integrity line in the project.

**Deep sequence models for forecasting, at this stage.** An LSTM trained on a handful of simulated events yields confident output with no basis. The transparent extrapolation with an honest error band is more defensible and likely no less accurate at these horizons.

**A photorealistic 3D digital twin in a game engine.** Weeks of work for a visual that a 2.5D map with live state satisfies. The bonus point is available at a small fraction of the cost via the venue graph.

**Drone integration.** Hardware dependency, DGCA regulatory constraints, undemoable indoors, and in direct tension with "minimum hardware dependencies."

**Wearables, RFID wristbands, or any distributed hardware.** Contradicts the core constraint of the brief. The phone in someone's pocket is the whole point.

**Real SMS or telecom integration.** DLT registration and operator agreements are a procurement timeline measured in days or weeks. Mock the channel, show the exact payload, label it mocked. Zero credibility cost, days saved.

**Real-time video streaming to the cloud.** Contradicts privacy, bandwidth, and cost simultaneously — and we deliberately do not need it, since features are computed at the edge. Building it would undermine our own architecture story.

**Audio-based scream or panic detection.** Superficially attractive, but the false-positive rate at concerts and festivals is catastrophic (cheering is indistinguishable from screaming to most classifiers), it needs microphones, and it raises fresh privacy problems. Defer with the reason stated.

**Social media scraping and sentiment analysis.** Noisy, rate-limited, geolocation-poor, and an easy place to overclaim. Low signal for high effort.

**Blockchain, for anything.** No.

**BLE mesh networking between phones.** The honest offline story — edge buffering, local server, cached clients, out-of-band channels — is achievable and sufficient. A mesh claim would be both hard and probably false.

**Native iOS and native Android and a separate web app.** Pick one mobile path and do it well. Three half-built clients demo worse than one working one.

**Authentication gold-plating.** OAuth providers, email verification, password reset flows, MFA. Necessary in production, invisible in a demo, and a reliable multi-hour sink.

**Microservices, Kubernetes, service meshes, message-broker sprawl.** A modular monolith with clean internal layer boundaries demonstrates the same architecture, deploys in one step, and does not fail on stage. We explain the scale path; we do not build it.

**Predicting which individuals will panic, or inferring emotional state from video.** Not scientifically supportable, ethically bad, and an instant credibility loss under questioning.

**Generic LLM-authored safety advice.** A recommendation engine that is a prompt is the specific failure mode the brief's "intelligent recommendations" requirement invites. Every recommendation must trace to measured preconditions.

**An admin UI for everything.** Configure the venue graph in a versioned file with a minimal editor for the parts we actually demo. A full CRUD console for capacities and thresholds is invisible on stage.

---

## 16. MVP Definition

### MVP — the smallest genuinely convincing solution

The test for MVP is whether it demonstrably answers the brief's own questions and shows a real prediction, not just a real dashboard. It must contain: the venue graph with zones, connections, and capacities; ingestion driving both a simulated source and at least one real video source; real density and optical-flow processing on the real source with integrity badges distinguishing real from simulated; the Crowd Instability Index and the speed-collapse detector; bottleneck detection by flow conservation; density trend forecasting with Time-To-Critical and uncertainty bands; the transparent risk engine with persistence, hysteresis, hazard overrides, confidence, and exact contribution decomposition; the five-level severity model with correct notification behaviour per level; the playbook recommendation engine with feasibility filtering, safety invariants, and stated triggering conditions; the control-room dashboard with live map, heat map, risk zones, trends, alert queue, per-zone detail, and explainability cards; a citizen client delivering geofenced multilingual action-framed warnings and incident reporting; a responder client with tasks, state transitions, and outcome capture; and alert adjudication.

Everything in that list serves an explicit official requirement. Nothing in it is decoration. MVP already includes Time-To-Critical and the instability index — because without them this is a crowd-density dashboard, which is explicitly out of scope, and it would not answer "is there crush risk in the next few minutes."

### Strong Version — MVP plus the differentiators

Add: Guardian Mode end to end, from on-device detection through self-clearance, Check-On Request, responder verification, and outcome capture; the intervention preview with before-and-after projections; risk-weighted safest-route computation; full offline and degraded-mode behaviour with a live outage demonstration and clean resynchronisation; multilingual announcement generation from pre-approved templates with back-translation and mandatory approval; corroboration scoring on citizen reports; and self-reported alert precision with proposed threshold recalibration.

**This is the target.** It covers every core requirement, delivers the innovation layer, and directly addresses four constraints (network outages, false alarm reduction, privacy, ease of use) that most entries will mention and few will demonstrate.

### Winning Version — Strong plus the bonuses, done honestly

Add: the venue model view presented as the digital twin foundation with live state; crowd movement simulation exposed as an operator-facing what-if tool including panic propagation, labelled as simulation with assumptions visible; a voice interface over a bounded set of read-only queries with on-screen confirmation for anything state-changing; a multilingual assistant strictly grounded in current system state that declines rather than speculates; and generative incident summaries traceable to source events, with the exported after-action report.

The reason to sequence bonuses last is not that they are unimportant — the brief awards points for them — but that each is only worth building on top of a real core. A voice interface over a fake risk engine is a party trick; over this one it is a genuine control-room affordance.

---

## 17. Demo Strategy

**Setup.** A festival or temple venue of eight to twelve zones. Two data paths running simultaneously and visibly distinguished: one or two zones fed by **real video** with live density and optical-flow processing, the rest by the **scripted simulator**. Integrity badges on every zone show which is which, unprompted. The scripted path exists so the narrative is reliable on stage; the real path exists so the CV is provably real. Saying both out loud, early, is a strength — it is the answer to the question every technical judge is already forming.

**0:00–0:30 · SAFE.** The venue map is green. Live camera panel shows real footage with the density overlay and flow vectors moving in real time. Trend charts are flat. Alert queue is empty. TTC reads "not projected." One sentence on the integrity badges. *Establishes: the system is running on real data and it does not cry wolf.*

**0:30–1:15 · Context event → WARNING.** A scheduled event fires — gates open and a train arrives. Inflow to Zone A jumps. Density climbs in A and downstream in Corridor D. Zone D goes LOW: outlined on the map, a quiet queue entry, no interruption. Then the important beat: mean speed in D starts *falling* while density keeps rising. A second signal family lights up, corroboration is satisfied, and D escalates to MODERATE. **TTC appears: "critical in ~9 min, moderate confidence."** The explainability card opens showing exact contributions. *Changes: the system has moved from describing to predicting, and it shows its work. Say that density alone would still read as fine here.*

**1:15–2:00 · HIGH RISK.** Deterioration continues: velocity dispersion rises, Corridor D's downstream gate hits capacity, the bottleneck engine names the cause as throttled outflow. Two Guardian Mode anomalies appear in Zone D and one corroborated citizen report arrives. The egress-adequacy hazard override fires and D goes HIGH — modal alert, audible, acknowledgement required, responders notified, geofenced citizens pushed a calm re-route message in three languages. TTC now reads two to four minutes. *Changes: multiple independent signal families agree, an override has bypassed the weighted score, and the system has demonstrated why corroboration and overrides both exist.*

**2:00–2:50 · INTERVENTION.** The recommendation panel shows a ranked list. Point out one rejected candidate and why — closing Gate 2 was rejected because it would drop egress below occupancy, a safety invariant. Select the top bundle: open Exit 5, halt inflow at Gates 2 and 3, one-way flow in Corridor 2, deploy four staff. **Open the intervention preview:** projected Zone D risk 78 → 41 by T+8, with Zone F rising 22 → 34 and that trade-off shown rather than hidden. Approve. Tasks land on a real responder phone on the table. The announcement composer renders the template in Hindi, English, and Marathi with back-translation displayed; approve and release. *Changes: a measured condition has become a justified, simulated, human-approved action with its side effects disclosed.*

**2:50–3:20 · Guardian Mode resolution.** On the demo phone, a Guardian anomaly triggers: the "Are you okay?" prompt with countdown appears, and is deliberately left unanswered. A Check-On Request — labelled `unverified` — appears in the operator queue as a low-priority verification task, not an incident. Dispatch to the nearest responder; the responder resolves it as "person assisted." *Say the limitation out loud: this does not detect a medical emergency, it detects that someone is not moving like the people around them, and it asks a human to look. Also note that in a full crush this signal disappears, which is why the instability index exists.*

**3:20–3:50 · Network outage.** Kill the cloud connection live. The dashboard flips to DEGRADED, naming exactly what is unavailable; confidence values drop; the control-room-local server keeps scoring and alerting for reachable sources; the citizen phone shows its cached map and still fires a geofence warning. Reconnect. Queued events sync, the timeline backfills in order, no duplicates. *Changes: nothing catastrophic — which is the point.*

**3:50–4:30 · RECOVERY.** Responder confirmations update the venue graph; inflow to D falls; density and instability decline. Severity de-escalates through the hysteresis band rather than snapping back, and CRITICAL-tier clearance requires the operator's explicit confirmation. Trends visibly return to baseline. *Changes: the system tracked the intervention's actual effect against its projection.*

**4:30–5:00 · LEARN.** Generate the incident summary from the event log, with source events traceable from each statement. Show the self-reported precision panel: alerts raised by severity, adjudicated outcomes, one honest false positive included, and the proposed threshold adjustment queued for administrator review rather than auto-applied. Export the after-action report.

**Closing line.** The full loop — sense, understand, predict, recommend, alert, respond, learn — ran in five minutes, on real computer vision for the camera zones, with every simulated input labelled, every threshold declared uncalibrated, and one false alarm shown rather than hidden.

**Contingency.** Pre-record the entire run as fallback video. Have the simulator runnable fully offline. Have the outage segment scripted so a genuine venue Wi-Fi failure becomes part of the demo rather than the end of it.

---

## 18. Evaluation Criteria

**Problem relevance.** Does the system answer all seven questions the brief poses? Does it demonstrate the reactive-to-predictive shift rather than asserting it? Does it engage with the stated ten-minute lead-time ambition specifically? *Evidence: map each of the seven questions to a visible product surface.*

**Technical depth.** Is the risk core grounded in crowd physics rather than arbitrary thresholds? Can we explain why density alone is insufficient, and show a case where it would mislead? Is the model choice per task justified — specifically, why density regression over detection, and optical flow over tracking? *Evidence: the two-zones-same-density comparison; the model rationale in §8.*

**Innovation.** Is there a capability here that other entries will not have? Is it a real capability rather than a reskin? *Evidence: instability index, Time-To-Critical, intervention preview, Guardian Mode, self-reported precision.*

**AI usage.** Is AI doing load-bearing work, or is it decoration? Is generative AI used where it belongs and kept out of where it does not? *Evidence: FR-175 and the deterministic risk core; generative AI confined to summaries, translation, and the assistant.*

**Real-world feasibility.** Does it work with existing infrastructure and no new hardware? What does a deployment actually cost and require? Has privacy law been considered? *Evidence: features-only architecture, CCTV reuse, phone-as-node option, DPDP-aware privacy posture with the honest note that legal review would be required.*

**Scalability.** What scales and what does not, and do we know which is which? *Evidence: per-source bandwidth is bytes not pixels; per-zone computation is independent; horizontal path described; ceilings stated as unmeasured rather than guessed.*

**Reliability.** What happens when a camera dies, the network drops, or data goes stale? Can the system say "I don't know"? *Evidence: the live outage demo; stale-source exclusion; confidence gating; the explicit insufficient-data state.*

**UX.** Could a police control-room operator use this under stress with minimal training? Is the most urgent thing always the most prominent thing? Does the citizen app avoid inducing the panic it aims to prevent? *Evidence: glanceable primary screen; redundant severity encoding; action-framed citizen copy as a stated safety requirement.*

**Explainability.** For any alert on screen, can we say exactly why, in numbers? For any recommendation, what triggered it and what is it projected to do? *Evidence: contribution decomposition is exact, not approximated, because the risk function is transparent by construction.*

**Demo impact.** Does the story land in five minutes? Is the escalation legible to a non-expert? Does it end on something memorable? *Evidence: the SAFE-to-LEARN arc with a stated change at each stage.*

**Integrity — the criterion we add for ourselves.** Is every claim defensible under hostile questioning? Have we labelled what is simulated, declared what is uncalibrated, and shown a false positive rather than hiding it? *This is the criterion most likely to separate us from entries that demo better and survive questioning worse.*

---

## 19. Open Technical Decisions

**Platform and stack.** Backend language and framework. Frontend framework. Mobile approach: native Android, cross-platform, or PWA — and the trade-off is real, since Guardian Mode needs reliable background motion and location access, which constrains the PWA option. Whether the CV pipeline is a separate process or in-process. Deployment target for the demo: laptop, cloud, or both, given that the outage demo needs a local path.

**Data and storage.** Time-series storage for the rolling feature windows. Event and audit store. Whether one database or separate stores. Retention windows per data category. Whether the venue graph lives in a database or a versioned file.

**Real-time transport.** WebSocket, SSE, or polling for the dashboard. Push mechanism for mobile. Whether a message broker is warranted at demo scale or is premature.

**Computer vision specifics.** Which density-regression model and which pretrained weights, weighed on CPU inference speed against accuracy. Frame sampling rate. Grid cell size, which materially affects the instability index. Ground-plane calibration method and how much manual effort it requires per camera. Whether any zone warrants detection-based counting instead.

**Risk engine parameters.** Initial family weights. Transfer-function breakpoints, including which published pedestrian level-of-service bands to adopt as starting points and how to cite them. The hazard override rule set. Persistence window counts and hysteresis gaps. The confidence formula and the suppression floor. Evaluation interval.

**Time-To-Critical method.** Extrapolation method and window length. How the uncertainty band is derived. When to return "unknown." How context events adjust the projection.

**Guardian Mode parameters.** Immobility window duration. Positional accuracy floor. Minimum neighbour sample count for a valid baseline. Self-clearance countdown length. Battery strategy and sampling cadence. Whether accelerometer data is used and how. Consent copy wording, which needs care.

**Simulation design.** Crowd model fidelity — agent-based, flow-based, or scripted zone-level series. Whether the same engine serves both demo data generation and intervention preview, which would be efficient but couples two concerns. Scenario authoring format.

**Recommendation engine.** Playbook schema. Initial library scope. Disruption cost scale. How lead times are estimated. The safety invariant set. Ranking formula.

**LLM integration.** Provider or local model. Whether the demo can depend on network access for it. Announcement template library scope and languages. Prompt and grounding strategy. Fallback when unavailable. Cost per event.

**Languages.** Which three for the MVP, and where translations come from — LLM, human, or a hybrid with human review of templates.

**Offline architecture.** What exactly runs on the local server versus cloud. Buffer sizes and eviction policy. Conflict resolution on sync. How the demo switches modes convincingly.

**Auth.** Minimum viable authentication for the demo versus what we describe for production. How roles are represented.

**Testing.** How we test a risk engine without ground truth. Scenario-based regression tests. Whether we build a replay harness, which would be valuable for both testing and demo reliability.

**Repository and process.** Monorepo or split. Module boundaries. Branching. Whether we write the venue graph schema first, given how many components depend on it.

> **Resolved since v1.0:** the venue graph schema is authored first. See `schemas/venue-graph.schema.json`.

---

## 20. Final Product Definition

CROWDShield is an AI-assisted early-warning and decision-support platform for crowd safety at large public gatherings. It estimates the physical state of a crowd — density, movement speed, flow direction, flow coherence, and flow instability — from existing camera infrastructure and consenting mobile devices, computing derived features at the edge and transmitting only those features rather than video, so that privacy, bandwidth cost, and tolerance of network failure are addressed by one architectural decision rather than three.

Over a topological model of the venue, it detects congestion hotspots, bottlenecks with their causes, blocked routes, counterflow, reverse movement, surges, and statistical deviations from each zone's learned baseline. It projects those measurements forward over a short horizon to produce a per-zone risk score and a Time-To-Critical estimate with an explicit uncertainty band, using a deterministic and auditable risk function that decomposes exactly into its contributing signals, applies hazard overrides for conditions that must not be averaged away, and reports confidence separately from risk so that uncertainty is never disguised as safety.

When risk rises, it generates interventions from a structured playbook library — not from a language model — where every recommendation is triggered by machine-checkable conditions, filtered for physical feasibility, rejected outright if it would violate a safety invariant, simulated against the venue model to project its effect and its side effects, and ranked with the time it needs to take effect weighed against the time available. Recommendations are presented to a human, who decides. Nothing executes on its own.

Alerts escalate through a five-tier severity model with persistence, hysteresis, corroboration requirements, and confidence gating to suppress false alarms, reaching control-room operators, field responders with dispatched verification and execution tasks, and attendees with location-scoped multilingual guidance that is deliberately action-framed rather than threat-framed. Responder outcomes and operator adjudications flow back in, so the system tracks whether interventions worked, measures and reports its own false-alarm rate, and proposes threshold recalibrations for human review rather than applying them silently.

As an experimental capability, it compares a consenting individual's movement state against that of the crowd immediately around them, and where the divergence is significant and confidence sufficient, raises an unverified anomaly for human verification after the individual has been given an on-device opportunity to clear it themselves. It does not, and cannot, determine a person's physical condition from a phone, and it says so.

Generative AI is confined to rendering decisions the deterministic core has already made: incident summaries traceable to logged events, announcement text filled into pre-approved templates and back-translation-checked, and grounded answers about current state. It has no influence on risk scoring or intervention selection.

The system degrades rather than fails — continuing to sense, score, and alert on a control-room-local deployment when the cloud is unreachable, serving cached guidance to offline phones, and resynchronising without duplication on recovery. Throughout, it labels what is simulated, declares which thresholds are uncalibrated, states what it does not know, and requires zero new hardware to begin operating.

**In one sentence:** CROWDShield converts existing cameras and the phones a crowd already carries into a measured, explainable, minutes-ahead warning system that tells authorities not merely that a crowd is dense, but that its flow is becoming unstable, how long they have, what to do, and how confident it is — while making its own uncertainty and its own errors visible rather than hiding them.

---

## Appendix A — Two standing risks to protect against

**The most important technical claim in this spec** is that density is a weak predictor and flow instability is a strong one. If we build that faithfully, we have a crush-prediction system; if we quietly fall back to density thresholds, we have the density dashboard this project explicitly rejects. It is the part to protect first when time gets short.

**The most important honesty risk** is Time-To-Critical. It is our best demo asset and the easiest thing in the system to accidentally turn into a lie. It has to ship as a range with a confidence level and a working "I don't know" state, or not ship at all.
