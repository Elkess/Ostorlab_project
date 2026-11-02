# MapleLens Mapper: Backend Schema

*There is no database or server. The "backend" is the in-memory data model plus the JSON input and output contracts (C1–C5). All files are read-only inputs; nothing is persisted.*

## 1. Data Model Overview

| Entity | Source | Cardinality |
|---|---|---|
| Input document | JSON file | 1 per run |
| Segment | `segments[]` | 0..n, validated all-or-nothing |
| Finding | `findings[]` | 0..n, validated per row |
| Result | output `results[]` | 1 per valid finding |
| Rejection | output `rejected[]` | 1 per invalid finding |
| Summary | output `summary` | 1 per run |

Relationship: a Finding matches zero or more Segments by exact `generated_file` and inclusive line range. A Result references the matching Segments by `segment_id`.

## 2. Input Schema

### 2.1 Input document

| Field | Type | Rule |
|---|---|---|
| `segments` | array | required, may be empty |
| `findings` | array | required, may be empty |
| other fields | any | ignored |

### 2.2 Segment

| Field | Type | Rules |
|---|---|---|
| `segment_id` | string | nonblank (contains a non-whitespace char); unique across all segments; preserved exactly |
| `generated_file` | string | nonblank; exact opaque path |
| `original_file` | string | nonblank; exact opaque path |
| `generated_start` | integer | >= 1; not boolean |
| `generated_end` | integer | >= 1; not boolean; `generated_start <= generated_end` |
| `original_start` | integer | >= 1; not boolean |

Any invalid segment, or a duplicate `segment_id`, fails the whole input (exit 2), even if no finding uses it.

### 2.3 Finding

| Field | Type | Rules |
|---|---|---|
| `finding_id` | string | nonblank; preserved; duplicates allowed |
| `generated_file` | string | nonblank; exact opaque path |
| `generated_line` | integer | >= 1; not boolean |

An invalid finding is a `rejected` entry, not a fatal error.

### 2.4 JSON Schema (draft 2020-12) for the fatal-level checks

This schema validates top-level shape and segments only. The nonblank rule, uniqueness, start <= end and the bool exclusion are enforced in code, because JSON Schema cannot express all of them and findings must be validated row by row instead.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["segments", "findings"],
  "properties": {
    "segments": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["segment_id", "generated_file", "original_file",
                     "generated_start", "generated_end", "original_start"],
        "properties": {
          "segment_id": { "type": "string", "pattern": "\\S" },
          "generated_file": { "type": "string", "pattern": "\\S" },
          "original_file": { "type": "string", "pattern": "\\S" },
          "generated_start": { "type": "integer", "minimum": 1 },
          "generated_end": { "type": "integer", "minimum": 1 },
          "original_start": { "type": "integer", "minimum": 1 }
        }
      }
    },
    "findings": { "type": "array" }
  }
}
```

## 3. Output Schema

### 3.1 Top level

| Field | Type | Notes |
|---|---|---|
| `results` | array of Result | valid findings, input order |
| `rejected` | array of Rejection | invalid findings, input order |
| `summary` | Summary | counts |

### 3.2 Result

| Field | Type | Notes |
|---|---|---|
| `row` | integer | one-based position in `findings` |
| `finding_id` | string | as input |
| `generated_file` | string | as input, byte-exact |
| `generated_line` | integer | as input |
| `status` | string | `mapped`, `unmapped`, or `ambiguous` |
| `matches` | array of string | sorted segment IDs; empty for unmapped |
| `target` | object or null | `{ "file": string, "line": integer }` only when mapped; otherwise null |

Target line: `original_start + generated_line - generated_start`.

### 3.3 Rejection

| Field | Type | Notes |
|---|---|---|
| `row` | integer | one-based |
| `finding_id` | string or null | the value only if it is a nonblank string |
| `reason` | string | human-readable; names the failing field |

### 3.4 Summary

| Field | Type | Invariant |
|---|---|---|
| `input_rows` | integer | `len(findings)` |
| `mapped` | integer | count of status mapped |
| `unmapped` | integer | count of status unmapped |
| `ambiguous` | integer | count of status ambiguous |
| `rejected_rows` | integer | `len(rejected)` |

Invariant: `mapped + unmapped + ambiguous + rejected_rows == input_rows`. The four classifications partition the input rows.

## 4. Example

Input (abridged):

```json
{
  "segments": [
    { "segment_id": "S1", "generated_file": "gen/a.js", "original_file": "src/a.ts",
      "generated_start": 10, "generated_end": 20, "original_start": 100 }
  ],
  "findings": [
    { "finding_id": "F1", "generated_file": "gen/a.js", "generated_line": 15 },
    { "finding_id": "F2", "generated_file": "gen/a.js", "generated_line": 21 },
    { "finding_id": "F3", "generated_file": "gen/a.js", "generated_line": true }
  ]
}
```

Output:

```json
{
  "results": [
    { "row": 1, "finding_id": "F1", "generated_file": "gen/a.js", "generated_line": 15,
      "status": "mapped", "matches": ["S1"], "target": { "file": "src/a.ts", "line": 105 } },
    { "row": 2, "finding_id": "F2", "generated_file": "gen/a.js", "generated_line": 21,
      "status": "unmapped", "matches": [], "target": null }
  ],
  "rejected": [
    { "row": 3, "finding_id": "F3", "reason": "generated_line must be a positive integer (got boolean)" }
  ],
  "summary": { "input_rows": 3, "mapped": 1, "unmapped": 1, "ambiguous": 0, "rejected_rows": 1 }
}
```

(Illustrative values only; they are not taken from the supplied fixtures.)

## 5. Internal Structures (Python)

```python
# index: exact generated_file string -> list of validated segments
index: dict[str, list[dict]]

# result row built fresh, input never mutated
result = {
  "row": i, "finding_id": fid, "generated_file": f, "generated_line": n,
  "status": status, "matches": sorted(ids), "target": target_or_None,
}
```

## 6. Data Integrity Rules

- No normalization of any path or ID: no strip, lower-case, `os.path`, or separator replacement. Whitespace-only is blank, but surrounding whitespace on valid values is preserved.
- Booleans are rejected wherever an integer is required (`type(v) is int`).
- Duplicate finding IDs are kept as separate rows; duplicate segment IDs are fatal.
- Inputs are never written to or modified; outputs are rebuilt on every run.
