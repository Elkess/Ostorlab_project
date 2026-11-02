# MapleLens Mapper decision and verification log

## Priorities and deferred work

I prioritized the contract-defined behavior in C1–C5: validate the complete segment map, reject bad finding rows without aborting the batch, map only exact inclusive matches, expose overlap evidence, and preserve stable output ordering. I kept the implementation as a standard-library CLI with a linear segment scan. A service, database, HTML report, interval index and additional CLI options were deferred because they are outside the core assessment scope.

## Obstacle and response

The important correctness risk was Python treating booleans as integers. The mapper uses an exact `type(value) is int` check, so `True` and `False` are rejected rather than interpreted as lines 1 and 0. Tests cover boolean values in both finding rows and segments.

## Validation and refinement

The primary fixture was checked against the required partition: 12 input rows, 7 mapped, 2 unmapped, 1 ambiguous and 2 rejected. The secondary fixture was run with the same code and reconciled by finding and segment IDs. In particular, `F04` becomes unmapped because `M02` moves from generated range 5–8 to 6–8; no mapping rule was changed to force the result to match the primary fixture. The constructed overlap boundary at generated line 4 is ambiguous and reports both matching segment IDs.

## Known limits and next step

The implementation uses a linear scan per finding and does not verify that original source files exist. That is intentional because the contract supplies coordinate metadata only. If production-scale maps were required, the next step would be an interval index keyed by the exact generated path, while retaining the same matching semantics.
