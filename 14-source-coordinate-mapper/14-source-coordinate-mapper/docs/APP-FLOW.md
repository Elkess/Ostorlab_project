# MapleLens Mapper: App Flow

*How a run moves from command line to exit code, and how each finding is decided.*

## 1. Actors and Entry Point

The user (engineer or reviewer) runs `python3 app.py --input <file>`. Library users call `map_locations(data)` directly with an already-parsed object.

## 2. End-to-End Run Flow

1. **Parse arguments.** `--help` prints usage and exits 0. A missing `--input` is a usage error.
2. **Read file.** Unreadable or missing file: message on stderr, **exit 2**, no stdout.
3. **Parse JSON.** Malformed JSON (for example `inputs/malformed-input.txt`): message on stderr, **exit 2**, no stdout.
4. **Validate top level.** Must be an object with arrays `segments` and `findings`. Otherwise **exit 2**.
5. **Validate every segment** (all of them, even unused ones). Any failure: **exit 2** naming the segment index and the field. Nothing partial is printed.
6. **Process findings in input order**, one-based row numbers (see section 3).
7. **Assemble output**: `results`, `rejected`, `summary`.
8. **Print JSON to stdout, exit 0**, even when some rows were rejected.

## 3. Per-Finding Decision Flow

```
row N
 |
 |-- not an object / bad finding_id / bad generated_file / bad generated_line (bool, float, <=0, string)
 |       -> rejected { row: N, finding_id: <nonblank string or null>, reason }  (continue)
 |
 |-- valid -> look up segments with EXACT generated_file
        |
        |-- 0 segments contain line  -> status unmapped,   matches [],           target null
        |-- 1 segment contains line  -> status mapped,     matches [ID],         target {file, line}
        |-- 2+ segments contain line -> status ambiguous,  matches [IDs sorted], target null
```

Mapped line formula: `original_line = original_start + generated_line - generated_start`. Range checks are inclusive on both ends. There is no nearest-segment fallback and no extrapolation across gaps.

## 4. Error and Exit-Code Flow

| Situation | Where detected | Result |
|---|---|---|
| File unreadable or missing | Read step | stderr message, exit 2 |
| Malformed JSON | Parse step | stderr message, exit 2 |
| Wrong top-level shape | Top-level validation | stderr message, exit 2 |
| Any invalid segment or duplicate ID | Segment validation | stderr message, exit 2 |
| Invalid finding row | Per-finding validation | `rejected` entry, run continues, exit 0 |
| Everything valid | End of run | JSON on stdout, exit 0 |

## 5. Second-Fixture Reconciliation Flow

1. Run `inputs/primary.json`, save output A.
2. Run `inputs/secondary.json` with the **same code**, save output B.
3. Join A and B by `finding_id` (and `row` where IDs repeat).
4. Classify each finding: **unchanged** (same status and target), **moved** (mapped in both, different target), **newly unmapped**, **newly ambiguous**, **newly mapped**, or **rejected in both**.
5. Report which segment IDs explain each change (`matches` in A versus B).
6. If a difference reveals a bug, refine the code, rerun primary and secondary, and log it.

## 6. Developer Workflow

1. Read contract C1–C5.
2. Validate the complete segment map before processing findings.
3. Write feature tests for each rule and preserve the documented CLI.
4. Run both fixtures and check the primary self-check (12 / 7 / 2 / 1 / 2).
5. Reconcile the secondary fixture.
6. Maintain the run guide, work log, AI-use note and walkthrough.
