# MapleLens Mapper: Product Requirements Document (PRD)

*Version 1.0 · Scope: Software Engineer Intern assessment exercise (fictional MapleLens)*

## 1. Overview

MapleLens scanners report finding locations in **generated source** (file + line). Engineers need the **original source** line. The Mapper is a reusable command-line tool and library function (`map_locations`) that translates generated coordinates to original coordinates using a supplied segment map, and clearly reports when the map cannot support a location.

Coordinate mapping does **not** confirm a vulnerability and does **not** recover missing mapping information.

## 2. Problem Statement

Without a trustworthy mapper, a teammate must guess where a generated-code finding lives in the real source. Guessing (nearest segment, first overlap, extrapolation) produces wrong triage. The tool must prefer an honest "unmapped" or "ambiguous" over an invented target.

## 3. Users and Needs

| User | Need |
|---|---|
| Security/triage engineer | Fast, correct original file/line per finding, plus evidence (segment IDs). |
| Teammate integrating the mapper | A reusable function and stable JSON output with documented exit codes. |
| Reviewer / assessor | Reproducible runs, tests, and reconciliation between map versions. |

## 4. Goals and Non-Goals

**Goals**
- Implement contract rules C1–C5 exactly.
- Deterministic JSON output; inputs never modified.
- Distinguish fatal map errors (exit 2) from rejected finding rows (exit 0).
- Run unchanged on the primary and secondary fixtures and reconcile differences.

**Non-goals**
- Web service, framework, database, public deployment.
- Reading source files, path normalization, or vulnerability confirmation.
- Extrapolating across gaps or repairing bad maps.

## 4.1 Functional Requirements

| ID | Requirement | Contract |
|---|---|---|
| FR1 | Validate top-level object with arrays `segments` and `findings`; any invalid segment fails the whole input (exit 2). | C1 |
| FR2 | Segment fields: nonblank strings `segment_id`, `generated_file`, `original_file`; positive integers (not bool) `generated_start`, `generated_end`, `original_start`; start <= end; unique IDs. Extra fields ignored. | C1 |
| FR3 | Paths are exact opaque strings: no trim, case fold, resolve, or separator change. | C2 |
| FR4 | Invalid finding rows produce one `rejected` diagnostic (one-based `row`, `finding_id` or null, readable `reason`) and processing continues. IDs never deduplicated. | C3 |
| FR5 | Match on exact generated path and inclusive range. 0 matches = `unmapped`; 2+ = `ambiguous`; 1 = `mapped` with `original_line = original_start + generated_line - generated_start`. | C4 |
| FR6 | Emit `results`, `rejected`, `summary` in input order with sorted `matches`; `target` only when mapped. | C5 |
| FR7 | Success exits 0 even with rejected rows; empty arrays valid; repeat runs identical. | C5 |
| FR8 | Fatal errors (bad schema, invalid segments, unreadable file, malformed JSON) exit 2, diagnostics on stderr, no stdout. | README |

## 5. Success Metrics

- Primary fixture: **12 rows → 7 mapped, 2 unmapped, 1 ambiguous, 2 rejected**.
- Summary counts partition input rows (mapped + unmapped + ambiguous + rejected = input_rows).
- Secondary fixture runs with no rule changes; every moved / unchanged / newly unknown finding reconciled by finding ID and segment ID.
- Test suite covers: endpoints, gaps, overlap, path case and separators, bool line values, reversed segments, empty arrays, malformed input, plus one constructed boundary and one fixed failing case.

## 6. Scoring Alignment (assessment)

Usable result 40 · Accuracy/verification 25 · Prioritization 20 · Communication/handoff 15.

## 7. Deliverables

Runnable source, tests, supplied inputs, run guide, decision/work log, AI-use note, and a 3–5 minute walkthrough (or equivalent text).

## 8. Risks and Assumptions

| Risk | Mitigation |
|---|---|
| Overlapping segments tempt "pick first" | Explicit `ambiguous` status, with tests. |
| Bool accepted as int in Python (`True == 1`) | Explicit `type(x) is int` / bool rejection. |
| Path "cleanup" breaks identity | No string transforms anywhere; tested with case and separator variants. |
| Fixture-only assumptions | Rules sourced only from contract; assumptions documented. |

## 9. Open Questions

- Should a finding row that is not an object be rejected with `finding_id` null? (Assumed yes, per C3.)
- Float values like `3.0` for integers: assumed invalid (not an integer type).
