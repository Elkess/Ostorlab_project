from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest

import app


def _run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "app.py", *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def _payload() -> dict[str, object]:
    return {
        "segments": [
            {
                "segment_id": "one",
                "generated_file": "generated.js",
                "generated_start": 2,
                "generated_end": 4,
                "original_file": "source.py",
                "original_start": 10,
            },
            {
                "segment_id": "overlap",
                "generated_file": "generated.js",
                "generated_start": 4,
                "generated_end": 6,
                "original_file": "other.py",
                "original_start": 20,
            },
        ],
        "findings": [],
    }


def _run_payload(payload: object) -> dict[str, object]:
    return app.map_locations(payload)  # type: ignore[arg-type]


class MapperTests(unittest.TestCase):
    def test_endpoints_and_gap(self) -> None:
        payload = _payload()
        payload["findings"] = [
            {"finding_id": "start", "generated_file": "generated.js", "generated_line": 2},
            {"finding_id": "end", "generated_file": "generated.js", "generated_line": 6},
            {"finding_id": "gap", "generated_file": "generated.js", "generated_line": 1},
            {"finding_id": "missing", "generated_file": "generated.js", "generated_line": 7},
        ]
        result = _run_payload(payload)
        self.assertEqual([item["status"] for item in result["results"]], ["mapped", "mapped", "unmapped", "unmapped"])
        self.assertEqual(result["results"][0]["target"], {"file": "source.py", "line": 10})
        self.assertEqual(result["results"][1]["target"], {"file": "other.py", "line": 22})

    def test_overlap_is_ambiguous_with_sorted_matches(self) -> None:
        payload = _payload()
        payload["findings"] = [{"finding_id": "f", "generated_file": "generated.js", "generated_line": 4}]
        result = _run_payload(payload)
        self.assertEqual(result["results"][0]["status"], "ambiguous")
        self.assertEqual(result["results"][0]["matches"], ["one", "overlap"])
        self.assertIsNone(result["results"][0]["target"])

    def test_paths_are_exact_and_case_sensitive(self) -> None:
        payload = _payload()
        payload["findings"] = [
            {"finding_id": "case", "generated_file": "Generated.js", "generated_line": 2},
            {"finding_id": "exact", "generated_file": "generated.js", "generated_line": 2},
        ]
        result = _run_payload(payload)
        self.assertEqual([item["status"] for item in result["results"]], ["unmapped", "mapped"])

    def test_invalid_finding_rows_are_rejected_and_counted(self) -> None:
        payload = _payload()
        payload["findings"] = [
            {"finding_id": "true", "generated_file": "generated.js", "generated_line": True},
            {"finding_id": "false", "generated_file": "generated.js", "generated_line": False},
            {"finding_id": "valid", "generated_file": "generated.js", "generated_line": 2},
            {"finding_id": " ", "generated_file": "generated.js", "generated_line": 2},
        ]
        result = _run_payload(payload)
        self.assertEqual(result["summary"], {
            "input_rows": 4, "mapped": 1, "unmapped": 0, "ambiguous": 0, "rejected_rows": 3,
        })
        self.assertEqual([item["finding_id"] for item in result["rejected"]], ["true", "false", None])

    def test_empty_arrays_return_zero_summary(self) -> None:
        result = _run_payload({"segments": [], "findings": []})
        self.assertEqual(result, {
            "results": [],
            "rejected": [],
            "summary": {"input_rows": 0, "mapped": 0, "unmapped": 0, "ambiguous": 0, "rejected_rows": 0},
        })

    def test_invalid_segments_are_fatal_even_when_unused(self) -> None:
        payload = {"segments": [{
            "segment_id": "bad",
            "generated_file": "x",
            "generated_start": 8,
            "generated_end": 2,
            "original_file": "y",
            "original_start": 1,
        }], "findings": []}
        with self.assertRaisesRegex(ValueError, "generated_start after generated_end"):
            _run_payload(payload)

    def test_top_level_schema_errors_are_fatal(self) -> None:
        invalid_payloads = [
            None,
            [],
            "not an object",
            {},
            {"segments": []},
            {"findings": []},
            {"segments": {}, "findings": []},
            {"segments": [], "findings": {}},
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                _run_payload(payload)

    def test_all_invalid_segment_fields_are_fatal(self) -> None:
        valid_segment = {
            "segment_id": "segment",
            "generated_file": "generated.js",
            "generated_start": 1,
            "generated_end": 2,
            "original_file": "source.py",
            "original_start": 10,
        }
        invalid_values = {
            "segment_id": "   ",
            "generated_file": "",
            "generated_start": True,
            "generated_end": False,
            "original_start": 1.5,
        }
        for field, value in invalid_values.items():
            segment = dict(valid_segment)
            segment[field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                _run_payload({"segments": [segment], "findings": []})

        for field, value in {
            "generated_start": "1",
            "generated_end": 0,
            "original_start": -1,
        }.items():
            segment = dict(valid_segment)
            segment[field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                _run_payload({"segments": [segment], "findings": []})

    def test_duplicate_segment_ids_are_fatal(self) -> None:
        first = _payload()["segments"][0]
        second = dict(first)
        second["generated_file"] = "other-generated.js"
        with self.assertRaisesRegex(ValueError, "duplicates segment_id"):
            _run_payload({"segments": [first, second], "findings": []})

    def test_paths_preserve_case_separators_and_surrounding_whitespace(self) -> None:
        payload = {
            "segments": [
                {
                    "segment_id": " spaced id ",
                    "generated_file": " dist/main.js ",
                    "generated_start": 1,
                    "generated_end": 1,
                    "original_file": " source.py ",
                    "original_start": 8,
                },
                {
                    "segment_id": "backslash",
                    "generated_file": "dist\\main.js",
                    "generated_start": 1,
                    "generated_end": 1,
                    "original_file": "windows.py",
                    "original_start": 20,
                },
            ],
            "findings": [
                {"finding_id": "exact-space", "generated_file": " dist/main.js ", "generated_line": 1},
                {"finding_id": "trimmed", "generated_file": "dist/main.js", "generated_line": 1},
                {"finding_id": "slash", "generated_file": "dist/main.js", "generated_line": 1},
                {"finding_id": "backslash", "generated_file": "dist\\main.js", "generated_line": 1},
            ],
        }
        result = _run_payload(payload)
        self.assertEqual([item["status"] for item in result["results"]], ["mapped", "unmapped", "unmapped", "mapped"])
        self.assertEqual(result["results"][0]["matches"], [" spaced id "])
        self.assertEqual(result["results"][0]["target"], {"file": " source.py ", "line": 8})
        self.assertEqual(result["results"][3]["target"], {"file": "windows.py", "line": 20})

    def test_overlap_is_ambiguous_even_when_targets_coincide(self) -> None:
        payload = {
            "segments": [
                {
                    "segment_id": "second",
                    "generated_file": "generated.js",
                    "generated_start": 3,
                    "generated_end": 4,
                    "original_file": "source.py",
                    "original_start": 10,
                },
                {
                    "segment_id": "first",
                    "generated_file": "generated.js",
                    "generated_start": 1,
                    "generated_end": 3,
                    "original_file": "source.py",
                    "original_start": 8,
                },
            ],
            "findings": [{"finding_id": "overlap", "generated_file": "generated.js", "generated_line": 3}],
        }
        result = _run_payload(payload)
        self.assertEqual(result["results"][0]["status"], "ambiguous")
        self.assertEqual(result["results"][0]["matches"], ["first", "second"])
        self.assertIsNone(result["results"][0]["target"])

    def test_invalid_finding_matrix_is_rejected_in_input_order(self) -> None:
        findings = [
            None,
            {"finding_id": "missing-file", "generated_line": 1},
            {"finding_id": "blank-file", "generated_file": "   ", "generated_line": 1},
            {"finding_id": "non-string-file", "generated_file": 1, "generated_line": 1},
            {"generated_file": "generated.js", "generated_line": 1},
            {"finding_id": "   ", "generated_file": "generated.js", "generated_line": 1},
            {"finding_id": "float", "generated_file": "generated.js", "generated_line": 1.5},
            {"finding_id": "string", "generated_file": "generated.js", "generated_line": "1"},
            {"finding_id": "zero", "generated_file": "generated.js", "generated_line": 0},
            {"finding_id": "negative", "generated_file": "generated.js", "generated_line": -1},
            {"finding_id": "bool", "generated_file": "generated.js", "generated_line": True},
        ]
        payload = _payload()
        payload["findings"] = findings
        result = _run_payload(payload)
        self.assertEqual([item["row"] for item in result["rejected"]], list(range(1, 12)))
        self.assertEqual(
            [item["finding_id"] for item in result["rejected"]],
            [None, "missing-file", "blank-file", "non-string-file", None, None, "float", "string", "zero", "negative", "bool"],
        )
        self.assertEqual(result["summary"], {
            "input_rows": 11,
            "mapped": 0,
            "unmapped": 0,
            "ambiguous": 0,
            "rejected_rows": 11,
        })
        self.assertTrue(all(item["reason"] for item in result["rejected"]))

    def test_duplicate_finding_ids_are_preserved_as_rows(self) -> None:
        payload = _payload()
        payload["findings"] = [
            {"finding_id": "duplicate", "generated_file": "generated.js", "generated_line": 2},
            {"finding_id": "duplicate", "generated_file": "generated.js", "generated_line": 7},
        ]
        result = _run_payload(payload)
        self.assertEqual([(item["row"], item["finding_id"]) for item in result["results"]], [
            (1, "duplicate"),
            (2, "duplicate"),
        ])

    def test_output_schema_partition_determinism_and_immutability(self) -> None:
        payload = _payload()
        payload["findings"] = [
            {"finding_id": "mapped", "generated_file": "generated.js", "generated_line": 2},
            {"finding_id": "invalid", "generated_file": "generated.js", "generated_line": False},
            {"finding_id": "unmapped", "generated_file": "generated.js", "generated_line": 7},
        ]
        original = copy.deepcopy(payload)
        first = _run_payload(payload)
        second = _run_payload(payload)
        self.assertEqual(first, second)
        self.assertEqual(payload, original)
        self.assertEqual(set(first), {"results", "rejected", "summary"})
        self.assertTrue(all(set(item) == {
            "row", "finding_id", "generated_file", "generated_line", "status", "matches", "target",
        } for item in first["results"]))
        self.assertTrue(all(set(item) == {"row", "finding_id", "reason"} for item in first["rejected"]))
        self.assertEqual(
            len(first["results"]) + len(first["rejected"]),
            first["summary"]["input_rows"],
        )
        self.assertEqual(
            {status: sum(item["status"] == status for item in first["results"])
             for status in ("mapped", "unmapped", "ambiguous")},
            {status: first["summary"][status] for status in ("mapped", "unmapped", "ambiguous")},
        )

    def test_secondary_fixture_uses_same_mapping_rules(self) -> None:
        result = _run_cli("--input", "inputs/secondary.json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        self.assertEqual(output["summary"], {
            "input_rows": 12,
            "mapped": 6,
            "unmapped": 3,
            "ambiguous": 1,
            "rejected_rows": 2,
        })
        by_id = {item["finding_id"]: item for item in output["results"]}
        self.assertEqual(by_id["F04"]["status"], "unmapped")
        self.assertEqual(by_id["F05"]["matches"], ["M02", "M03"])
        self.assertEqual(by_id["F07"]["target"], {"file": "src/jobs.py", "line": 101})

    def test_cli_missing_file_is_fatal_without_stdout(self) -> None:
        result = _run_cli("--input", "inputs/does-not-exist.json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)

    def test_cli_malformed_json_is_fatal_without_stdout(self) -> None:
        result = _run_cli("--input", "inputs/malformed-input.txt")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)

    def test_cli_outputs_successful_json(self) -> None:
        result = _run_cli("--input", "inputs/primary.json")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["summary"], {
            "input_rows": 12,
            "mapped": 7,
            "unmapped": 2,
            "ambiguous": 1,
            "rejected_rows": 2,
        })
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
