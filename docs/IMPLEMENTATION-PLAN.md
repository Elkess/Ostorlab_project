# MapleLens Mapper: Implementation Plan

*A prioritized, verifiable plan for the 24-hour window. Realistic effort is a few focused hours; the rest of the window is buffer for verification and writing. Hours worked are not scored.*

## 1. Guiding Priorities

1. **Correct core (C1–C5)** before anything optional.
2. **Verification** (tests, both fixtures, reconciliation) before polish.
3. **Honest handoff** (run guide, work log, AI note, walkthrough).
4. **Defer** HTML report, `--summary`, interval index, and any extra features.

## 2. Phases

| Phase | Work | Est. time | Exit criteria |
|---|---|---|---|
| 0. Setup | Run `--help`, the test suite and the primary fixture | 15 min | Environment and baseline behavior are verified |
| 1. Read and plan | Read C1–C5, open both fixtures, list edge cases | 30 min | Written edge-case list |
| 2. Validation | `is_nonblank_str`, `is_pos_int`, `validate_segments`, `validate_finding`, `MapError` | 45 min | Unit tests for each rule pass |
| 3. Mapping core | `build_index`, `map_locations`, output assembly, summary | 45 min | Hand-checked mapped, unmapped, ambiguous cases |
| 4. CLI | Wire `main`, exit codes and stderr messages | 20 min | Fatal inputs exit 2 with empty stdout; valid runs exit 0 |
| 5. Tests | Replace placeholder assertion; add feature tests (section 4) | 60 min | Suite green, covers every contract rule |
| 6. Primary check | Run primary; confirm 12 / 7 / 2 / 1 / 2 | 15 min | Counts match and partition |
| 7. Secondary | Run secondary unchanged; reconcile by finding ID and segment ID | 45 min | Every moved, unchanged, newly unknown location explained |
| 8. Refinement | Log one failing case or validation that forced a fix; rerun both fixtures | 20 min | Fix recorded with evidence |
| 9. Handoff | README run commands, run guide, work log, AI-use note, walkthrough text or recording | 60 min | All four submission items present |

## 3. Suggested File Layout

```
candidate/
  app.py                 # CLI + map_locations (or split into mapper.py)
  inputs/                # supplied fixtures, contract, malformed-input.txt
  tests/app_test.py      # feature tests (replace placeholder assertion)
  README.md              # accurate run commands
  docs/
    run-guide.md
    work-log.md
    ai-use-note.md
    walkthrough.md       # or a 3-5 minute recording
```

If logic grows, split into `mapper.py` (pure functions) and keep `app.py` as a thin CLI, preserving the documented `--input` and `--help` options.

## 4. Test Checklist (tick as completed)

- [x] Endpoint hits: `generated_start` and `generated_end` map; start-1 and end+1 do not.
- [x] Gap between segments is `unmapped`; no extrapolation.
- [x] Overlap yields `ambiguous` with sorted IDs, even when targets coincide.
- [x] Path case difference and `/` versus `\` are different files.
- [x] Whitespace-only path or ID is blank; surrounding spaces preserved on valid values.
- [x] `True`/`False` rejected as `generated_line` (row rejected) and as segment integers (fatal).
- [x] Float, string, zero, negative lines rejected.
- [x] Reversed segment (`start > end`) is fatal even if unused.
- [x] Duplicate `segment_id` is fatal.
- [x] Unused invalid segment still fails the input.
- [x] Empty `segments` and `findings`: `results`, `rejected` empty, counts all zero, exit 0.
- [x] Malformed JSON (`inputs/malformed-input.txt`): exit 2, empty stdout, readable stderr.
- [x] Missing file: exit 2.
- [x] Non-object finding row: rejected with `finding_id` null.
- [x] Duplicate finding IDs preserved as separate rows.
- [x] Output key set exactly matches C5; summary partitions input rows.
- [x] Two runs produce identical output; input object unchanged (deep copy comparison).
- [x] Constructed boundary: adjacent segments sharing an edge line are `ambiguous` at that line.
- [x] Primary fixture: 12 / 7 / 2 / 1 / 2.
- [x] Secondary fixture runs without rule changes.

## 5. Milestones and Definition of Done

| Milestone | Done when |
|---|---|
| M1 Core works | Primary fixture output matches the self-check |
| M2 Verified | Test suite green and covers every C1–C5 rule |
| M3 Reconciled | Secondary fixture explained row by row |
| M4 Handed off | Run guide, work log, AI note, walkthrough present; README commands accurate |

## 6. Risks and Responses

| Risk | Response |
|---|---|
| Scope creep into services or UI | Check the PRD non-goals; defer stretch items |
| `True` accepted as an integer | Use `type(v) is int`; add a bool test early |
| Accidental normalization of paths | Review code for `strip`, `lower`, `os.path` on identity values |
| Picking first overlap | Test ambiguity explicitly, including coincident targets |
| Time pressure at the end | Write the work log while building, not after |

## 7. Work Log Template

- **Priorities and deferred items:** what was built first, what was skipped and why.
- **Obstacle and response:** one real problem and how it was handled.
- **Validation and refinement:** one failing case or check, the fix, and rerun evidence (cite `finding_id`, `segment_id`, or row numbers).
- **Known limits and next step:** linear scan, no source-file verification; next step could be an interval index or a reconciliation report.

## 8. AI-Use Note Template

One concrete example of AI output that was accepted, corrected, or rejected, and how it was checked against the contract or an executed test. If AI was not used, say so. Do not invent a failure and do not paste full prompt histories or secrets.

## 9. Walkthrough Outline (3–5 minutes)

1. **Workflow (about 1.5 min):** input, validation, lookup, output, exit codes.
2. **One edge case (about 1 min):** for example an overlap that is `ambiguous` rather than first-match.
3. **Evidence (about 1 min):** terminal run of both fixtures and the test suite.
4. **Limits and next step (about 30 s).**
