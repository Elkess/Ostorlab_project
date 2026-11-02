from __future__ import annotations

import argparse
import json
import sys


def _is_nonblank_string(value: object) -> bool:
    return isinstance(value, str) and any(not character.isspace() for character in value)


def _is_positive_integer(value: object) -> bool:
    return type(value) is int and value > 0


def _validate_segments(segments: object) -> list[dict[str, object]]:
    if not isinstance(segments, list):
        raise ValueError("segments must be an array")

    validated: list[dict[str, object]] = []
    segment_ids: set[str] = set()
    required_strings = ("segment_id", "generated_file", "original_file")
    required_numbers = ("generated_start", "generated_end", "original_start")

    for row, segment in enumerate(segments, start=1):
        if not isinstance(segment, dict):
            raise ValueError(f"segment row {row} must be an object")

        for field in required_strings:
            if not _is_nonblank_string(segment.get(field)):
                raise ValueError(f"segment row {row} has invalid {field}")
        for field in required_numbers:
            if not _is_positive_integer(segment.get(field)):
                raise ValueError(f"segment row {row} has invalid {field}")

        segment_id = segment["segment_id"]
        generated_start = segment["generated_start"]
        generated_end = segment["generated_end"]
        if segment_id in segment_ids:
            raise ValueError(f"segment row {row} duplicates segment_id {segment_id!r}")
        if generated_start > generated_end:
            raise ValueError(f"segment row {row} has generated_start after generated_end")

        segment_ids.add(segment_id)
        validated.append(segment)

    return validated


def _finding_id_for_rejection(finding: object) -> str | None:
    if isinstance(finding, dict):
        finding_id = finding.get("finding_id")
        if _is_nonblank_string(finding_id):
            return finding_id
    return None


def _validate_finding(finding: object, row: int) -> tuple[str, str, int] | str:
    if not isinstance(finding, dict):
        return "finding must be an object"
    if not _is_nonblank_string(finding.get("finding_id")):
        return "finding_id must be a nonblank string"
    if not _is_nonblank_string(finding.get("generated_file")):
        return "generated_file must be a nonblank string"
    if not _is_positive_integer(finding.get("generated_line")):
        return "generated_line must be a positive integer"
    return (
        finding["finding_id"],
        finding["generated_file"],
        finding["generated_line"],
    )


def map_locations(
    payload: object, arguments: argparse.Namespace | None = None
) -> dict[str, object]:
    """Validate a mapping payload and map each valid finding to its source location."""
    del arguments
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object")
    if "segments" not in payload or "findings" not in payload:
        raise ValueError("input must contain segments and findings arrays")
    if not isinstance(payload["findings"], list):
        raise ValueError("findings must be an array")

    segments = _validate_segments(payload["segments"])
    results: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    counts = {"mapped": 0, "unmapped": 0, "ambiguous": 0}

    for row, finding in enumerate(payload["findings"], start=1):
        validated = _validate_finding(finding, row)
        if isinstance(validated, str):
            rejected.append(
                {
                    "row": row,
                    "finding_id": _finding_id_for_rejection(finding),
                    "reason": validated,
                }
            )
            continue

        finding_id, generated_file, generated_line = validated
        matching_segments = [
            segment
            for segment in segments
            if segment["generated_file"] == generated_file
            and segment["generated_start"] <= generated_line <= segment["generated_end"]
        ]
        matches = sorted(segment["segment_id"] for segment in matching_segments)

        if len(matching_segments) == 0:
            status = "unmapped"
            target = None
        elif len(matching_segments) > 1:
            status = "ambiguous"
            target = None
        else:
            status = "mapped"
            segment = matching_segments[0]
            target = {
                "file": segment["original_file"],
                "line": segment["original_start"]
                + generated_line
                - segment["generated_start"],
            }
        counts[status] += 1
        results.append(
            {
                "row": row,
                "finding_id": finding_id,
                "generated_file": generated_file,
                "generated_line": generated_line,
                "status": status,
                "matches": matches,
                "target": target,
            }
        )

    return {
        "results": results,
        "rejected": rejected,
        "summary": {
            "input_rows": len(payload["findings"]),
            "mapped": counts["mapped"],
            "unmapped": counts["unmapped"],
            "ambiguous": counts["ambiguous"],
            "rejected_rows": len(rejected),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Map generated-source finding coordinates.")
    parser.add_argument("--input", default="inputs/primary.json", help="UTF-8 mapping JSON")
    arguments = parser.parse_args()
    try:
        with open(arguments.input, encoding="utf-8") as input_file:
            payload = json.load(input_file)
        result = map_locations(payload, arguments)
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
