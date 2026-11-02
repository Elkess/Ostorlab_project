# MapleLens Mapper: Technical Requirements Document (TRD)

*Version 1.0 · Companion to the PRD; rules come from the mapping contract C1–C5.*

## 1. Technical Scope

A single-process Python CLI plus an importable pure function `map_locations(data) -> dict`. No network, no database, no third-party packages, no source files read.

## 2. Environment

| Item | Requirement |
|---|---|
| Language | Python 3.10+ |
| Dependencies | Standard library only (`json`, `argparse`, `sys`, `unittest`) |
| OS | Any with Python; paths treated as opaque strings |
| Entry point | `python3 app.py --input <file>` |
| Tests | `python3 -m unittest discover -s tests -p '*_test.py' -v` |

## 3. Architecture

Three layers, kept separate so the core is testable without the CLI:

1. **I/O layer (CLI):** parses `--input`, reads the file, loads JSON, prints JSON to stdout, prints diagnostics to stderr, sets exit code.
2. **Validation layer:** `validate_input` (top-level schema), `validate_segments` (all segments, fatal), `validate_finding` (per row, non-fatal).
3. **Mapping core:** `map_locations` builds a per-file index and resolves each valid finding to `mapped`, `unmapped`, or `ambiguous`.

```
file -> json.load -> validate top-level -> validate ALL segments (fatal)
     -> for each finding row: validate -> rejected | lookup -> result
     -> assemble results / rejected / summary -> stdout JSON
```

## 4. Module and Function Design

| Function | Responsibility | Failure behavior |
|---|---|---|
| `MapError(Exception)` | Fatal map/schema error | Caught in CLI, exit 2 |
| `is_nonblank_str(v)` | `type(v) is str` and `v.strip() != ""`; original string never modified | returns bool |
| `is_pos_int(v)` | `type(v) is int` and `v > 0` (rejects bool, float) | returns bool |
| `validate_segments(raw)` | Check every segment; unique IDs; start <= end | raises `MapError` with segment index and field |
| `validate_finding(row)` | Returns `(ok, finding_id_or_None, reason)` | never raises |
| `build_index(segments)` | Dict keyed by exact `generated_file` -> list of segments | n/a |
| `map_locations(data)` | Full pipeline, returns output dict | raises `MapError` for fatal cases only |
| `main(argv)` | CLI wrapper, exit codes | maps exceptions to exit 2 |

## 5. Algorithm (C4)

For each valid finding `(file, line)`:

1. `candidates = index.get(file, [])` (exact string key, no normalization).
2. `matches = [s for s in candidates if s.generated_start <= line <= s.generated_end]`.
3. `len == 0` -> `unmapped`, target null. `len == 1` -> `mapped`, `line_out = original_start + line - generated_start`, target `{file: original_file, line: line_out}`. `len >= 2` -> `ambiguous`, target null.
4. `matches` field = sorted segment IDs (all statuses; empty list for unmapped).

Complexity: O(F x S_file). Acceptable for the assessment; an interval index is a documented next step, not required.

## 6. Validation Rules Summary

**Fatal (exit 2, stdout empty):** input not an object; `segments` or `findings` not arrays; any invalid segment (even if unused); duplicate segment IDs; start > end; non-positive or bool/float integers; blank strings; unreadable file; malformed JSON.

**Non-fatal (rejected row, exit 0):** finding not an object; blank or non-string `finding_id` or `generated_file`; `generated_line` not a positive non-bool integer. `finding_id` in the diagnostic is the value only when it is a nonblank string, else null.

## 7. Exit Codes and Streams

| Code | Meaning | stdout | stderr |
|---|---|---|---|
| 0 | Success (including rejected rows) | JSON | empty |
| 2 | Fatal input error | empty | readable message |
| 3 | Reserved; not used by the completed implementation | n/a | n/a |

## 8. Determinism and Immutability

- Results follow input order; `matches` sorted; JSON keys emitted in a fixed order (explicitly built dicts, or `sort_keys=True` consistently).
- Never mutate the parsed input; build new dicts.
- No timestamps, randomness, or environment-dependent output.

## 9. Test Strategy

| Area | Cases |
|---|---|
| Boundaries | line == start, line == end, start-1, end+1, single-line segment |
| Gaps | line between two segments is `unmapped` (no extrapolation) |
| Overlap | two matching segments -> `ambiguous` even if targets equal |
| Path identity | case difference, `/` vs `\`, leading/trailing space, preserved bytes |
| Types | `True`/`False` as line or segment ints, floats, strings, negative, zero |
| Segments | reversed range, duplicate IDs, missing field, unused-but-invalid segment -> exit 2 |
| Output | key set per C5, summary partition, input order, empty arrays, repeat-run equality, input unchanged |
| CLI | `--help`, missing file, malformed JSON (exit 2, no stdout), primary and secondary counts |
| Constructed boundary | e.g. adjacent segments sharing an edge line (`end` of A equals `start` of B) -> `ambiguous` |

One failing case found during validation must be recorded in the work log along with the fix (for example, `True` passing an `isinstance(x, int)` check).

## 10. Second-Fixture Reconciliation

A small script or documented procedure runs both fixtures with the same code, then diffs by `finding_id` and `segment_id`, classifying each location as *unchanged*, *moved* (different target), *newly unmapped/ambiguous*, or *newly mapped*. No rule changes are allowed to make results match.

## 11. Known Limits

Linear scan per finding; no source-file verification; duplicate finding IDs are preserved by design.
