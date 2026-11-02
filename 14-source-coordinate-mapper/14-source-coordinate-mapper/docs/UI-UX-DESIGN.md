# MapleLens Mapper: UI/UX Design Brief

*The core product is a CLI and JSON contract, so "UI" here means the terminal experience, the JSON output ergonomics, and an optional lightweight HTML report for the walkthrough. The web service is out of scope; the report is a stretch only.*

## 1. Design Principles

- **Honesty over helpfulness.** An unmapped or ambiguous result is shown plainly; never dress a guess as a target.
- **Evidence first.** Every result carries its segment IDs so the reader can verify.
- **Predictable.** Same input gives the same bytes; stable ordering and key order.
- **Quiet success, loud failure.** Success prints only JSON to stdout; fatal errors print one readable line to stderr.
- **Machine and human friendly.** JSON for tools, optional pretty summary for people.

## 2. CLI Experience

**Usage**

```
usage: app.py [-h] --input INPUT

Map generated-source finding locations to original source lines.

options:
  -h, --help     show this help message and exit
  --input INPUT  path to a JSON file with "segments" and "findings"
```

**Fatal error message pattern** (stderr, one line, no stack trace): `error: <what is wrong> (<where>)`

Examples:
- `error: segments[2].generated_end must be >= generated_start (got 10 < 20)`
- `error: cannot read inputs/missing.json: No such file or directory`
- `error: malformed JSON in inputs/malformed-input.txt: line 4 column 9`

**Rejected row reason pattern** (readable, specific, names the field): `generated_line must be a positive integer (got boolean)`, `finding_id must be a nonblank string`.

## 3. JSON Output Style

- Two-space indentation; UTF-8; trailing newline.
- Fixed key order: `results`, `rejected`, `summary`. Inside a result: `row`, `finding_id`, `generated_file`, `generated_line`, `status`, `matches`, `target`.
- Status vocabulary is exactly `mapped`, `unmapped`, `ambiguous` (lowercase). `rejected` is a separate list, not a status.
- `target` is `{ "file": ..., "line": ... }` or `null`, never an empty object.

## 4. Optional Terminal Summary (stretch)

A `--summary` flag could print a compact human table to stderr while JSON stays on stdout. Do not add it unless the core is done and tested.

| Status | Symbol | Color (ANSI, only when stderr is a TTY) |
|---|---|---|
| mapped | OK | Green |
| unmapped | -- | Yellow |
| ambiguous | ?? | Magenta |
| rejected | !! | Red |

Color is never the only signal; each status also has a text label. Honor `NO_COLOR`.

## 5. Optional HTML Report (walkthrough aid)

A single self-contained page that renders the same JSON as a table, for the recorded walkthrough only.

### Color palette

| Role | Light | Dark | Use |
|---|---|---|---|
| Background | #FAF8F5 | #17181A | Page |
| Surface | #FFFFFF | #222427 | Cards, table |
| Text | #1F2328 | #E6E8EA | Body |
| Muted text | #5B6470 | #9AA3AD | Labels |
| Maple (primary) | #B7312C | #E0625B | Brand, headings accent |
| Mapped | #1F7A4D | #4CC38A | Success badge |
| Unmapped | #A66A00 | #F0B34A | Warning badge |
| Ambiguous | #6B4FBB | #A78BFA | Ambiguity badge |
| Rejected | #B3261E | #FF8A80 | Error badge |
| Border | #E3DED6 | #34373B | Dividers |

All text/background pairs target at least WCAG AA contrast (4.5:1).

### Typography

| Use | Font stack | Size / weight |
|---|---|---|
| Headings | `system-ui, -apple-system, "Segoe UI", sans-serif` | 24 / 600, 18 / 600 |
| Body | same as above | 15 / 400, line-height 1.5 |
| Paths, IDs, lines | `ui-monospace, "SF Mono", Menlo, Consolas, monospace` | 13 / 400 |

No web fonts required; system stacks only.

### Components

- **Summary bar:** five counters (input rows, mapped, unmapped, ambiguous, rejected) that visibly sum to the input total.
- **Results table:** columns Row, Finding ID, Generated location, Status badge, Matches (chips), Target. Row order preserved.
- **Status badge:** pill, text label plus color.
- **Segment chip:** monospace pill showing a segment ID.
- **Rejected panel:** list of row, finding ID or `null`, reason.
- **Reconciliation view (secondary fixture):** two-column diff by finding ID with change tags: unchanged, moved, newly unmapped, newly ambiguous, newly mapped.

### Style

Flat, low-ornament, 8px spacing scale, 6px corner radius, 1px borders, no shadows or animation. Table scrolls horizontally inside its own container on narrow screens. Paths are displayed exactly as given (no trimming, no case change), with whitespace made visible if present.

## 6. Accessibility

- Never rely on color alone; always a text label.
- Keyboard-navigable table; semantic `<table>`, `<th scope>`.
- Respect `prefers-color-scheme` and `NO_COLOR`.
- Error text is plain language, no jargon beyond field names.

## 7. Content Tone

Short, factual, no apologies or hype. Example: `Row 7: unmapped. No segment covers inventory/Gen.java line 412.` rather than "Sorry, we couldn't find it."
