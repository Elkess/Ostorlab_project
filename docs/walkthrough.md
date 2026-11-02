# MapleLens Mapper walkthrough

This text is the accessible walkthrough equivalent for the requested short recording.

## 1. Workflow

The CLI accepts a JSON file through `--input`. It first parses the JSON and requires an object containing `segments` and `findings` arrays. Every segment is validated before any finding is processed. Invalid segment data is fatal: the command prints a diagnostic to stderr and exits 2.

Valid finding rows are processed in their original order. A finding matches only segments with the exact same generated path and an inclusive generated line range. One match produces a mapped target using the one-based offset formula. No matches produce `unmapped`; multiple matches produce `ambiguous` and list all sorted segment IDs. Invalid finding rows are retained as row-level diagnostics, so the batch still exits 0.

The successful JSON output contains `results`, `rejected` and `summary`. Results and diagnostics preserve input row numbers and finding IDs. The input is never modified.

## 2. Edge case

In the primary fixture, finding `F05` is on generated line 7 of `dist/main.js`. Both `M02` (range 5–8) and `M03` (range 7–9) contain that line. The mapper therefore returns status `ambiguous`, matches `M02` and `M03`, and a null target. It does not select the first segment. Finding `F03` demonstrates the opposite case: generated line 4 is a gap and remains unmapped rather than being extrapolated to a nearby segment.

## 3. Execution evidence

The automated suite passes and covers mapping boundaries, gaps, overlaps, exact path identity, bool and numeric validation, malformed JSON, output shape, immutability and both fixtures. The primary run returns summary counts 12 input rows, 7 mapped, 2 unmapped, 1 ambiguous and 2 rejected. The secondary run returns 6 mapped, 3 unmapped, 1 ambiguous and 2 rejected. In the secondary fixture, `F04` becomes unmapped because `M02` starts at generated line 6, while `F01` and `F02` move because `M01` has a different original start.

Malformed JSON and a missing file both return exit 2 with no stdout. The implementation deliberately remains a small standard-library CLI; source-file existence checks and performance indexing are outside this contract.
