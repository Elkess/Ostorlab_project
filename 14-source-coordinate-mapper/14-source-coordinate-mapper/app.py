# Import the requested compatibility feature so the mapper contract can use modern type annotations safely.
from __future__ import annotations

# Import this standard-library module because the mapper contract needs its functionality.
import argparse
# Import this standard-library module because the mapper contract needs its functionality.
import json
# Import this standard-library module because the mapper contract needs its functionality.
import sys


# Define this helper or entry point so the mapper contract has a focused, reusable operation.
def _is_nonblank_string(value: object) -> bool:
    # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
    return isinstance(value, str) and any(not character.isspace() for character in value)


# Define this helper or entry point so the mapper contract has a focused, reusable operation.
def _is_positive_integer(value: object) -> bool:
    # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
    return type(value) is int and value > 0


# Define this helper or entry point so the mapper contract has a focused, reusable operation.
def _validate_segments(segments: object) -> list[dict[str, object]]:
    # Check this condition because the mapper contract requires different behavior for this case.
    if not isinstance(segments, list):
        # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
        raise ValueError("segments must be an array")

    # Store or update this value so the next statements can implement the mapper contract.
    validated: list[dict[str, object]] = []
    # Store or update this value so the next statements can implement the mapper contract.
    segment_ids: set[str] = set()
    # Store or update this value so the next statements can implement the mapper contract.
    required_strings = ("segment_id", "generated_file", "original_file")
    # Store or update this value so the next statements can implement the mapper contract.
    required_numbers = ("generated_start", "generated_end", "original_start")

    # Iterate through these values so the mapper contract processes every relevant row without skipping input.
    for row, segment in enumerate(segments, start=1):
        # Check this condition because the mapper contract requires different behavior for this case.
        if not isinstance(segment, dict):
            # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
            raise ValueError(f"segment row {row} must be an object")

        # Iterate through these values so the mapper contract processes every relevant row without skipping input.
        for field in required_strings:
            # Check this condition because the mapper contract requires different behavior for this case.
            if not _is_nonblank_string(segment.get(field)):
                # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
                raise ValueError(f"segment row {row} has invalid {field}")
        # Iterate through these values so the mapper contract processes every relevant row without skipping input.
        for field in required_numbers:
            # Check this condition because the mapper contract requires different behavior for this case.
            if not _is_positive_integer(segment.get(field)):
                # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
                raise ValueError(f"segment row {row} has invalid {field}")

        # Store or update this value so the next statements can implement the mapper contract.
        segment_id = segment["segment_id"]
        # Store or update this value so the next statements can implement the mapper contract.
        generated_start = segment["generated_start"]
        # Store or update this value so the next statements can implement the mapper contract.
        generated_end = segment["generated_end"]
        # Check this condition because the mapper contract requires different behavior for this case.
        if segment_id in segment_ids:
            # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
            raise ValueError(f"segment row {row} duplicates segment_id {segment_id!r}")
        # Check this condition because the mapper contract requires different behavior for this case.
        if generated_start > generated_end:
            # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
            raise ValueError(f"segment row {row} has generated_start after generated_end")

        # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
        segment_ids.add(segment_id)
        # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
        validated.append(segment)

    # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
    return validated


# Define this helper or entry point so the mapper contract has a focused, reusable operation.
def _finding_id_for_rejection(finding: object) -> str | None:
    # Check this condition because the mapper contract requires different behavior for this case.
    if isinstance(finding, dict):
        # Store or update this value so the next statements can implement the mapper contract.
        finding_id = finding.get("finding_id")
        # Check this condition because the mapper contract requires different behavior for this case.
        if _is_nonblank_string(finding_id):
            # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
            return finding_id
    # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
    return None


# Define this helper or entry point so the mapper contract has a focused, reusable operation.
def _validate_finding(finding: object, row: int) -> tuple[str, str, int] | str:
    # Check this condition because the mapper contract requires different behavior for this case.
    if not isinstance(finding, dict):
        # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
        return "finding must be an object"
    # Check this condition because the mapper contract requires different behavior for this case.
    if not _is_nonblank_string(finding.get("finding_id")):
        # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
        return "finding_id must be a nonblank string"
    # Check this condition because the mapper contract requires different behavior for this case.
    if not _is_nonblank_string(finding.get("generated_file")):
        # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
        return "generated_file must be a nonblank string"
    # Check this condition because the mapper contract requires different behavior for this case.
    if not _is_positive_integer(finding.get("generated_line")):
        # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
        return "generated_line must be a positive integer"
    # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
    return (
        # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
        finding["finding_id"],
        # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
        finding["generated_file"],
        # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
        finding["generated_line"],
    # Close or continue this structure so the surrounding the mapper contract expression remains valid.
    )


# Define this helper or entry point so the mapper contract has a focused, reusable operation.
def map_locations(
    # Store or update this value so the next statements can implement the mapper contract.
    payload: object, arguments: argparse.Namespace | None = None
# Begin this block because the mapper contract needs the statements nested beneath it.
) -> dict[str, object]:
    # Provide this literal value as part of the data required by the mapper contract.
    """Validate a mapping payload and map each valid finding to its source location."""
    # Discard this intentionally unused compatibility value so it cannot affect the mapping behavior.
    del arguments
    # Check this condition because the mapper contract requires different behavior for this case.
    if not isinstance(payload, dict):
        # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
        raise ValueError("input must be a JSON object")
    # Check this condition because the mapper contract requires different behavior for this case.
    if "segments" not in payload or "findings" not in payload:
        # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
        raise ValueError("input must contain segments and findings arrays")
    # Check this condition because the mapper contract requires different behavior for this case.
    if not isinstance(payload["findings"], list):
        # Reject this invalid case because the mapper contract cannot safely continue with the supplied value.
        raise ValueError("findings must be an array")

    # Store or update this value so the next statements can implement the mapper contract.
    segments = _validate_segments(payload["segments"])
    # Store or update this value so the next statements can implement the mapper contract.
    results: list[dict[str, object]] = []
    # Store or update this value so the next statements can implement the mapper contract.
    rejected: list[dict[str, object]] = []
    # Store or update this value so the next statements can implement the mapper contract.
    counts = {"mapped": 0, "unmapped": 0, "ambiguous": 0}

    # Iterate through these values so the mapper contract processes every relevant row without skipping input.
    for row, finding in enumerate(payload["findings"], start=1):
        # Store or update this value so the next statements can implement the mapper contract.
        validated = _validate_finding(finding, row)
        # Check this condition because the mapper contract requires different behavior for this case.
        if isinstance(validated, str):
            # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
            rejected.append(
                # Close or continue this structure so the surrounding the mapper contract expression remains valid.
                {
                    # Provide this literal value as part of the data required by the mapper contract.
                    "row": row,
                    # Provide this literal value as part of the data required by the mapper contract.
                    "finding_id": _finding_id_for_rejection(finding),
                    # Provide this literal value as part of the data required by the mapper contract.
                    "reason": validated,
                # Close or continue this structure so the surrounding the mapper contract expression remains valid.
                }
            # Close or continue this structure so the surrounding the mapper contract expression remains valid.
            )
            # Skip only this invalid row and continue processing so the mapper contract preserves valid input results.
            continue

        # Store or update this value so the next statements can implement the mapper contract.
        finding_id, generated_file, generated_line = validated
        # Store or update this value so the next statements can implement the mapper contract.
        matching_segments = [
            # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
            segment
            # Iterate through these values so the mapper contract processes every relevant row without skipping input.
            for segment in segments
            # Check this condition because the mapper contract requires different behavior for this case.
            if segment["generated_file"] == generated_file
            # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
            and segment["generated_start"] <= generated_line <= segment["generated_end"]
        # Close or continue this structure so the surrounding the mapper contract expression remains valid.
        ]
        # Store or update this value so the next statements can implement the mapper contract.
        matches = sorted(segment["segment_id"] for segment in matching_segments)

        # Check this condition because the mapper contract requires different behavior for this case.
        if len(matching_segments) == 0:
            # Store or update this value so the next statements can implement the mapper contract.
            status = "unmapped"
            # Store or update this value so the next statements can implement the mapper contract.
            target = None
        # Check this condition because the mapper contract requires different behavior for this case.
        elif len(matching_segments) > 1:
            # Store or update this value so the next statements can implement the mapper contract.
            status = "ambiguous"
            # Store or update this value so the next statements can implement the mapper contract.
            target = None
        # Handle the remaining valid branch so the mapper contract is complete and deterministic.
        else:
            # Store or update this value so the next statements can implement the mapper contract.
            status = "mapped"
            # Store or update this value so the next statements can implement the mapper contract.
            segment = matching_segments[0]
            # Store or update this value so the next statements can implement the mapper contract.
            target = {
                # Provide this literal value as part of the data required by the mapper contract.
                "file": segment["original_file"],
                # Provide this literal value as part of the data required by the mapper contract.
                "line": segment["original_start"]
                # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
                + generated_line
                # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
                - segment["generated_start"],
            # Close or continue this structure so the surrounding the mapper contract expression remains valid.
            }
        # Store or update this value so the next statements can implement the mapper contract.
        counts[status] += 1
        # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
        results.append(
            # Close or continue this structure so the surrounding the mapper contract expression remains valid.
            {
                # Provide this literal value as part of the data required by the mapper contract.
                "row": row,
                # Provide this literal value as part of the data required by the mapper contract.
                "finding_id": finding_id,
                # Provide this literal value as part of the data required by the mapper contract.
                "generated_file": generated_file,
                # Provide this literal value as part of the data required by the mapper contract.
                "generated_line": generated_line,
                # Provide this literal value as part of the data required by the mapper contract.
                "status": status,
                # Provide this literal value as part of the data required by the mapper contract.
                "matches": matches,
                # Provide this literal value as part of the data required by the mapper contract.
                "target": target,
            # Close or continue this structure so the surrounding the mapper contract expression remains valid.
            }
        # Close or continue this structure so the surrounding the mapper contract expression remains valid.
        )

    # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
    return {
        # Provide this literal value as part of the data required by the mapper contract.
        "results": results,
        # Provide this literal value as part of the data required by the mapper contract.
        "rejected": rejected,
        # Provide this literal value as part of the data required by the mapper contract.
        "summary": {
            # Provide this literal value as part of the data required by the mapper contract.
            "input_rows": len(payload["findings"]),
            # Provide this literal value as part of the data required by the mapper contract.
            "mapped": counts["mapped"],
            # Provide this literal value as part of the data required by the mapper contract.
            "unmapped": counts["unmapped"],
            # Provide this literal value as part of the data required by the mapper contract.
            "ambiguous": counts["ambiguous"],
            # Provide this literal value as part of the data required by the mapper contract.
            "rejected_rows": len(rejected),
        # Close or continue this structure so the surrounding the mapper contract expression remains valid.
        },
    # Close or continue this structure so the surrounding the mapper contract expression remains valid.
    }


# Define this helper or entry point so the mapper contract has a focused, reusable operation.
def main() -> int:
    # Store or update this value so the next statements can implement the mapper contract.
    parser = argparse.ArgumentParser(description="Map generated-source finding coordinates.")
    # Execute this statement as part of the mapper contract; keeping it explicit makes the intended behavior reviewable.
    parser.add_argument("--input", default="inputs/primary.json", help="UTF-8 mapping JSON")
    # Store or update this value so the next statements can implement the mapper contract.
    arguments = parser.parse_args()
    # Start protected processing so the mapper contract can convert expected failures into the documented result.
    try:
        # Use this managed block so the mapper contract acquires and releases the resource safely.
        with open(arguments.input, encoding="utf-8") as input_file:
            # Store or update this value so the next statements can implement the mapper contract.
            payload = json.load(input_file)
        # Store or update this value so the next statements can implement the mapper contract.
        result = map_locations(payload, arguments)
        # Write this output because the mapper contract requires a stable user-visible result or diagnostic.
        print(json.dumps(result, indent=2, sort_keys=True))
    # Handle this expected failure so the mapper contract reports it clearly instead of emitting partial output.
    except (OSError, UnicodeError, ValueError) as error:
        # Write this output because the mapper contract requires a stable user-visible result or diagnostic.
        print(f"error: {error}", file=sys.stderr)
        # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
        return 2
    # Return this value so the caller can continue the mapper contract with the required result or diagnostic.
    return 0


# Only run the command-line entry point when this file is executed directly, not when imported.
if __name__ == "__main__":
    # Propagate the computed status to the operating system so the CLI contract is observable.
    sys.exit(main())
