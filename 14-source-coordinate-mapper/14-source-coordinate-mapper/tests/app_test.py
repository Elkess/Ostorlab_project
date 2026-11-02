# Import the requested compatibility feature so the test scenario can use modern type annotations safely.
from __future__ import annotations

# Import this standard-library module because the test scenario needs its functionality.
import copy
# Import this standard-library module because the test scenario needs its functionality.
import json
# Import this standard-library module because the test scenario needs its functionality.
import subprocess
# Import this standard-library module because the test scenario needs its functionality.
import sys
# Import this standard-library module because the test scenario needs its functionality.
import unittest

# Import this standard-library module because the test scenario needs its functionality.
import app


# Define this helper or entry point so the test scenario has a focused, reusable operation.
def _run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    # Return this value so the caller can continue the test scenario with the required result or diagnostic.
    return subprocess.run(
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        [sys.executable, "app.py", *arguments],
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        capture_output=True,
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        text=True,
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        check=False,
    # Close or continue this structure so the surrounding the test scenario expression remains valid.
    )


# Define this helper or entry point so the test scenario has a focused, reusable operation.
def _payload() -> dict[str, object]:
    # Return this value so the caller can continue the test scenario with the required result or diagnostic.
    return {
        # Provide this literal value as part of the data required by the test scenario.
        "segments": [
            # Close or continue this structure so the surrounding the test scenario expression remains valid.
            {
                # Provide this literal value as part of the data required by the test scenario.
                "segment_id": "one",
                # Provide this literal value as part of the data required by the test scenario.
                "generated_file": "generated.js",
                # Provide this literal value as part of the data required by the test scenario.
                "generated_start": 2,
                # Provide this literal value as part of the data required by the test scenario.
                "generated_end": 4,
                # Provide this literal value as part of the data required by the test scenario.
                "original_file": "source.py",
                # Provide this literal value as part of the data required by the test scenario.
                "original_start": 10,
            # Close or continue this structure so the surrounding the test scenario expression remains valid.
            },
            # Close or continue this structure so the surrounding the test scenario expression remains valid.
            {
                # Provide this literal value as part of the data required by the test scenario.
                "segment_id": "overlap",
                # Provide this literal value as part of the data required by the test scenario.
                "generated_file": "generated.js",
                # Provide this literal value as part of the data required by the test scenario.
                "generated_start": 4,
                # Provide this literal value as part of the data required by the test scenario.
                "generated_end": 6,
                # Provide this literal value as part of the data required by the test scenario.
                "original_file": "other.py",
                # Provide this literal value as part of the data required by the test scenario.
                "original_start": 20,
            # Close or continue this structure so the surrounding the test scenario expression remains valid.
            },
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ],
        # Provide this literal value as part of the data required by the test scenario.
        "findings": [],
    # Close or continue this structure so the surrounding the test scenario expression remains valid.
    }


# Define this helper or entry point so the test scenario has a focused, reusable operation.
def _run_payload(payload: object) -> dict[str, object]:
    # Return this value so the caller can continue the test scenario with the required result or diagnostic.
    return app.map_locations(payload)  # type: ignore[arg-type]


# Define this test class so related checks for the test scenario stay grouped together.
class MapperTests(unittest.TestCase):
    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_endpoints_and_gap(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = _payload()
        # Store or update this value so the next statements can implement the test scenario.
        payload["findings"] = [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "start", "generated_file": "generated.js", "generated_line": 2},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "end", "generated_file": "generated.js", "generated_line": 6},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "gap", "generated_file": "generated.js", "generated_line": 1},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "missing", "generated_file": "generated.js", "generated_line": 7},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ]
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual([item["status"] for item in result["results"]], ["mapped", "mapped", "unmapped", "unmapped"])
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][0]["target"], {"file": "source.py", "line": 10})
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][1]["target"], {"file": "other.py", "line": 22})

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_overlap_is_ambiguous_with_sorted_matches(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = _payload()
        # Store or update this value so the next statements can implement the test scenario.
        payload["findings"] = [{"finding_id": "f", "generated_file": "generated.js", "generated_line": 4}]
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][0]["status"], "ambiguous")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][0]["matches"], ["one", "overlap"])
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertIsNone(result["results"][0]["target"])

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_paths_are_exact_and_case_sensitive(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = _payload()
        # Store or update this value so the next statements can implement the test scenario.
        payload["findings"] = [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "case", "generated_file": "Generated.js", "generated_line": 2},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "exact", "generated_file": "generated.js", "generated_line": 2},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ]
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual([item["status"] for item in result["results"]], ["unmapped", "mapped"])

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_invalid_finding_rows_are_rejected_and_counted(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = _payload()
        # Store or update this value so the next statements can implement the test scenario.
        payload["findings"] = [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "true", "generated_file": "generated.js", "generated_line": True},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "false", "generated_file": "generated.js", "generated_line": False},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "valid", "generated_file": "generated.js", "generated_line": 2},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": " ", "generated_file": "generated.js", "generated_line": 2},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ]
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["summary"], {
            # Provide this literal value as part of the data required by the test scenario.
            "input_rows": 4, "mapped": 1, "unmapped": 0, "ambiguous": 0, "rejected_rows": 3,
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        })
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual([item["finding_id"] for item in result["rejected"]], ["true", "false", None])

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_empty_arrays_return_zero_summary(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload({"segments": [], "findings": []})
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result, {
            # Provide this literal value as part of the data required by the test scenario.
            "results": [],
            # Provide this literal value as part of the data required by the test scenario.
            "rejected": [],
            # Provide this literal value as part of the data required by the test scenario.
            "summary": {"input_rows": 0, "mapped": 0, "unmapped": 0, "ambiguous": 0, "rejected_rows": 0},
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        })

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_invalid_segments_are_fatal_even_when_unused(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = {"segments": [{
            # Provide this literal value as part of the data required by the test scenario.
            "segment_id": "bad",
            # Provide this literal value as part of the data required by the test scenario.
            "generated_file": "x",
            # Provide this literal value as part of the data required by the test scenario.
            "generated_start": 8,
            # Provide this literal value as part of the data required by the test scenario.
            "generated_end": 2,
            # Provide this literal value as part of the data required by the test scenario.
            "original_file": "y",
            # Provide this literal value as part of the data required by the test scenario.
            "original_start": 1,
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        }], "findings": []}
        # Use this managed block so the test scenario acquires and releases the resource safely.
        with self.assertRaisesRegex(ValueError, "generated_start after generated_end"):
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            _run_payload(payload)

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_top_level_schema_errors_are_fatal(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        invalid_payloads = [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            None,
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            [],
            # Provide this literal value as part of the data required by the test scenario.
            "not an object",
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"segments": []},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"findings": []},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"segments": {}, "findings": []},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"segments": [], "findings": {}},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ]
        # Iterate through these values so the test scenario processes every relevant row without skipping input.
        for payload in invalid_payloads:
            # Use this managed block so the test scenario acquires and releases the resource safely.
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
                _run_payload(payload)

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_all_invalid_segment_fields_are_fatal(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        valid_segment = {
            # Provide this literal value as part of the data required by the test scenario.
            "segment_id": "segment",
            # Provide this literal value as part of the data required by the test scenario.
            "generated_file": "generated.js",
            # Provide this literal value as part of the data required by the test scenario.
            "generated_start": 1,
            # Provide this literal value as part of the data required by the test scenario.
            "generated_end": 2,
            # Provide this literal value as part of the data required by the test scenario.
            "original_file": "source.py",
            # Provide this literal value as part of the data required by the test scenario.
            "original_start": 10,
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        }
        # Store or update this value so the next statements can implement the test scenario.
        invalid_values = {
            # Provide this literal value as part of the data required by the test scenario.
            "segment_id": "   ",
            # Provide this literal value as part of the data required by the test scenario.
            "generated_file": "",
            # Provide this literal value as part of the data required by the test scenario.
            "generated_start": True,
            # Provide this literal value as part of the data required by the test scenario.
            "generated_end": False,
            # Provide this literal value as part of the data required by the test scenario.
            "original_start": 1.5,
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        }
        # Iterate through these values so the test scenario processes every relevant row without skipping input.
        for field, value in invalid_values.items():
            # Store or update this value so the next statements can implement the test scenario.
            segment = dict(valid_segment)
            # Store or update this value so the next statements can implement the test scenario.
            segment[field] = value
            # Use this managed block so the test scenario acquires and releases the resource safely.
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
                _run_payload({"segments": [segment], "findings": []})

        # Iterate through these values so the test scenario processes every relevant row without skipping input.
        for field, value in {
            # Provide this literal value as part of the data required by the test scenario.
            "generated_start": "1",
            # Provide this literal value as part of the data required by the test scenario.
            "generated_end": 0,
            # Provide this literal value as part of the data required by the test scenario.
            "original_start": -1,
        # Begin this block because the test scenario needs the statements nested beneath it.
        }.items():
            # Store or update this value so the next statements can implement the test scenario.
            segment = dict(valid_segment)
            # Store or update this value so the next statements can implement the test scenario.
            segment[field] = value
            # Use this managed block so the test scenario acquires and releases the resource safely.
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
                _run_payload({"segments": [segment], "findings": []})

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_duplicate_segment_ids_are_fatal(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        first = _payload()["segments"][0]
        # Store or update this value so the next statements can implement the test scenario.
        second = dict(first)
        # Store or update this value so the next statements can implement the test scenario.
        second["generated_file"] = "other-generated.js"
        # Use this managed block so the test scenario acquires and releases the resource safely.
        with self.assertRaisesRegex(ValueError, "duplicates segment_id"):
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            _run_payload({"segments": [first, second], "findings": []})

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_paths_preserve_case_separators_and_surrounding_whitespace(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = {
            # Provide this literal value as part of the data required by the test scenario.
            "segments": [
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                {
                    # Provide this literal value as part of the data required by the test scenario.
                    "segment_id": " spaced id ",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_file": " dist/main.js ",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_start": 1,
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_end": 1,
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_file": " source.py ",
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_start": 8,
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                },
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                {
                    # Provide this literal value as part of the data required by the test scenario.
                    "segment_id": "backslash",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_file": "dist\\main.js",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_start": 1,
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_end": 1,
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_file": "windows.py",
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_start": 20,
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                },
            # Close or continue this structure so the surrounding the test scenario expression remains valid.
            ],
            # Provide this literal value as part of the data required by the test scenario.
            "findings": [
                # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
                {"finding_id": "exact-space", "generated_file": " dist/main.js ", "generated_line": 1},
                # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
                {"finding_id": "trimmed", "generated_file": "dist/main.js", "generated_line": 1},
                # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
                {"finding_id": "slash", "generated_file": "dist/main.js", "generated_line": 1},
                # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
                {"finding_id": "backslash", "generated_file": "dist\\main.js", "generated_line": 1},
            # Close or continue this structure so the surrounding the test scenario expression remains valid.
            ],
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        }
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual([item["status"] for item in result["results"]], ["mapped", "unmapped", "unmapped", "mapped"])
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][0]["matches"], [" spaced id "])
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][0]["target"], {"file": " source.py ", "line": 8})
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][3]["target"], {"file": "windows.py", "line": 20})

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_overlap_is_ambiguous_even_when_targets_coincide(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = {
            # Provide this literal value as part of the data required by the test scenario.
            "segments": [
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                {
                    # Provide this literal value as part of the data required by the test scenario.
                    "segment_id": "second",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_file": "generated.js",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_start": 3,
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_end": 4,
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_file": "source.py",
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_start": 10,
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                },
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                {
                    # Provide this literal value as part of the data required by the test scenario.
                    "segment_id": "first",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_file": "generated.js",
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_start": 1,
                    # Provide this literal value as part of the data required by the test scenario.
                    "generated_end": 3,
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_file": "source.py",
                    # Provide this literal value as part of the data required by the test scenario.
                    "original_start": 8,
                # Close or continue this structure so the surrounding the test scenario expression remains valid.
                },
            # Close or continue this structure so the surrounding the test scenario expression remains valid.
            ],
            # Provide this literal value as part of the data required by the test scenario.
            "findings": [{"finding_id": "overlap", "generated_file": "generated.js", "generated_line": 3}],
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        }
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][0]["status"], "ambiguous")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["results"][0]["matches"], ["first", "second"])
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertIsNone(result["results"][0]["target"])

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_invalid_finding_matrix_is_rejected_in_input_order(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        findings = [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            None,
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "missing-file", "generated_line": 1},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "blank-file", "generated_file": "   ", "generated_line": 1},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "non-string-file", "generated_file": 1, "generated_line": 1},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"generated_file": "generated.js", "generated_line": 1},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "   ", "generated_file": "generated.js", "generated_line": 1},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "float", "generated_file": "generated.js", "generated_line": 1.5},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "string", "generated_file": "generated.js", "generated_line": "1"},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "zero", "generated_file": "generated.js", "generated_line": 0},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "negative", "generated_file": "generated.js", "generated_line": -1},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "bool", "generated_file": "generated.js", "generated_line": True},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ]
        # Store or update this value so the next statements can implement the test scenario.
        payload = _payload()
        # Store or update this value so the next statements can implement the test scenario.
        payload["findings"] = findings
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual([item["row"] for item in result["rejected"]], list(range(1, 12)))
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            [item["finding_id"] for item in result["rejected"]],
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            [None, "missing-file", "blank-file", "non-string-file", None, None, "float", "string", "zero", "negative", "bool"],
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        )
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result["summary"], {
            # Provide this literal value as part of the data required by the test scenario.
            "input_rows": 11,
            # Provide this literal value as part of the data required by the test scenario.
            "mapped": 0,
            # Provide this literal value as part of the data required by the test scenario.
            "unmapped": 0,
            # Provide this literal value as part of the data required by the test scenario.
            "ambiguous": 0,
            # Provide this literal value as part of the data required by the test scenario.
            "rejected_rows": 11,
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        })
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertTrue(all(item["reason"] for item in result["rejected"]))

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_duplicate_finding_ids_are_preserved_as_rows(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = _payload()
        # Store or update this value so the next statements can implement the test scenario.
        payload["findings"] = [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "duplicate", "generated_file": "generated.js", "generated_line": 2},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "duplicate", "generated_file": "generated.js", "generated_line": 7},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ]
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual([(item["row"], item["finding_id"]) for item in result["results"]], [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            (1, "duplicate"),
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            (2, "duplicate"),
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        ])

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_output_schema_partition_determinism_and_immutability(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        payload = _payload()
        # Store or update this value so the next statements can implement the test scenario.
        payload["findings"] = [
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "mapped", "generated_file": "generated.js", "generated_line": 2},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "invalid", "generated_file": "generated.js", "generated_line": False},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {"finding_id": "unmapped", "generated_file": "generated.js", "generated_line": 7},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        ]
        # Store or update this value so the next statements can implement the test scenario.
        original = copy.deepcopy(payload)
        # Store or update this value so the next statements can implement the test scenario.
        first = _run_payload(payload)
        # Store or update this value so the next statements can implement the test scenario.
        second = _run_payload(payload)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(first, second)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(payload, original)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(set(first), {"results", "rejected", "summary"})
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertTrue(all(set(item) == {
            # Provide this literal value as part of the data required by the test scenario.
            "row", "finding_id", "generated_file", "generated_line", "status", "matches", "target",
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        } for item in first["results"]))
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertTrue(all(set(item) == {"row", "finding_id", "reason"} for item in first["rejected"]))
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            len(first["results"]) + len(first["rejected"]),
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            first["summary"]["input_rows"],
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        )
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {status: sum(item["status"] == status for item in first["results"])
             # Iterate through these values so the test scenario processes every relevant row without skipping input.
             for status in ("mapped", "unmapped", "ambiguous")},
            # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
            {status: first["summary"][status] for status in ("mapped", "unmapped", "ambiguous")},
        # Close or continue this structure so the surrounding the test scenario expression remains valid.
        )

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_secondary_fixture_uses_same_mapping_rules(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_cli("--input", "inputs/secondary.json")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.returncode, 0)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.stderr, "")
        # Store or update this value so the next statements can implement the test scenario.
        output = json.loads(result.stdout)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(output["summary"], {
            # Provide this literal value as part of the data required by the test scenario.
            "input_rows": 12,
            # Provide this literal value as part of the data required by the test scenario.
            "mapped": 6,
            # Provide this literal value as part of the data required by the test scenario.
            "unmapped": 3,
            # Provide this literal value as part of the data required by the test scenario.
            "ambiguous": 1,
            # Provide this literal value as part of the data required by the test scenario.
            "rejected_rows": 2,
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        })
        # Store or update this value so the next statements can implement the test scenario.
        by_id = {item["finding_id"]: item for item in output["results"]}
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(by_id["F04"]["status"], "unmapped")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(by_id["F05"]["matches"], ["M02", "M03"])
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(by_id["F07"]["target"], {"file": "src/jobs.py", "line": 101})

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_cli_missing_file_is_fatal_without_stdout(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_cli("--input", "inputs/does-not-exist.json")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.returncode, 2)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.stdout, "")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertIn("error:", result.stderr)

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_cli_malformed_json_is_fatal_without_stdout(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_cli("--input", "inputs/malformed-input.txt")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.returncode, 2)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.stdout, "")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertIn("error:", result.stderr)

    # Define this helper or entry point so the test scenario has a focused, reusable operation.
    def test_cli_outputs_successful_json(self) -> None:
        # Store or update this value so the next statements can implement the test scenario.
        result = _run_cli("--input", "inputs/primary.json")
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.returncode, 0)
        # Store or update this value so the next statements can implement the test scenario.
        output = json.loads(result.stdout)
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(output["summary"], {
            # Provide this literal value as part of the data required by the test scenario.
            "input_rows": 12,
            # Provide this literal value as part of the data required by the test scenario.
            "mapped": 7,
            # Provide this literal value as part of the data required by the test scenario.
            "unmapped": 2,
            # Provide this literal value as part of the data required by the test scenario.
            "ambiguous": 1,
            # Provide this literal value as part of the data required by the test scenario.
            "rejected_rows": 2,
        # Execute this statement as part of the test scenario; keeping it explicit makes the intended behavior reviewable.
        })
        # Assert this expected outcome so the test proves the relevant rule in the test scenario.
        self.assertEqual(result.stderr, "")


# Only run the command-line entry point when this file is executed directly, not when imported.
if __name__ == "__main__":
    # Invoke the test framework so the file can run as a standalone test module.
    unittest.main()
