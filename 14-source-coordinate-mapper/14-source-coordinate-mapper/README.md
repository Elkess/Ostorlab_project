# Map generated-source finding locations

This is one Software Engineer Intern assessment with a **24-hour** window. Your recruiter assigns one exercise from the bank. Your 24 hours start when you click **Start** on the link in your invitation email; the exercise zip becomes available at that moment. Send your submission back within 24 hours of clicking Start. You are not expected to work for the full 24 hours: organize your own working time and breaks within the window. There are no surprise messages or overnight availability requirements, and hours worked are not scored. Follow-through and verification matter more than hours or volume.

At fictional MapleLens, a scanner reports generated-source coordinates. A teammate needs a reusable mapper to locate original source lines and see when the supplied map cannot support a location. Coordinate mapping does not confirm a vulnerability or recover missing mapping information.

All companies, tenants, assets and product behavior here are **fictional assessment facts**. The supplied fixtures are the authoritative universe. Outside research is optional and cannot affect marks. Do not contact real systems, send real messages, publish, or use production credentials.

## Supplied inputs and setup

You need basic Python, JSON, CLI use, tests, validation and line-offset arithmetic. Python **3.10 or later**, its standard library, and any local editor are sufficient; no packages, accounts, paid tools, web access or company framework are needed.

- [Mapper CLI and reusable implementation](app.py): safe JSON loading and C1–C5 coordinate mapping.
- [Primary fixture](inputs/primary.json): six mapping segments and twelve findings.
- [Second fixture](inputs/secondary.json): regenerated map, unchanged finding rows.
- [Mapping contract](inputs/mapping-contract.md): authoritative schema, coordinate and output rules C1–C5.
- [Malformed input](inputs/malformed-input.txt): deliberately truncated JSON for error handling.
- [Automated tests](tests/app_test.py): contract, fixture, CLI, determinism and error-handling coverage.

From the exported `candidate/` directory:

```sh
python3 --version
python3 app.py --help
python3 -m unittest discover -s tests -p '*_test.py' -v
python3 app.py --input inputs/primary.json
```

The implementation is complete: the test suite should pass, valid fixture runs should emit JSON on stdout with exit **0**, and fatal input errors should emit a readable diagnostic on stderr with exit **2** and no stdout. The CLI preserves the documented `--input` and `--help` options.

## Core task and observable acceptance criteria

Build a usable feature implementing C1–C5. Use JSON on stdout for successful runs, readable diagnostics on stderr for fatal errors, and the documented exit codes. Explain any assumptions without silently changing the rules.

1. Implement reusable `map_locations` lookup per generated file and line. Validate all segments before processing findings; distinguish fatal map errors from rejected finding rows. Preserve finding IDs and row references.
2. Translate only when exactly one segment matches. Return the matching segment IDs as evidence for mapped or ambiguous results; leave unknown targets null. Preserve exact path identity, inclusive endpoints and one-based offsets.
3. Produce the complete C5 output schema and partition counts with stable ordering. Re-running must give identical output without modifying inputs. Empty inputs return empty arrays and zero counts.
4. Add meaningful automated checks of results and errors: endpoints, gaps, overlap, path case/separators, bool line values, reversed segments, empty arrays and malformed input. Include a boundary you construct and one failing case you fix or validation that causes refinement.
5. Run the same implementation and tests on the second fixture without rewriting mapping rules. Reconcile every moved, unchanged or newly unknown location by finding and segment ID; record any refinement and rerun primary.

Primary self-check: **12 input rows, 7 mapped, 2 unmapped, 1 ambiguous, 2 rejected**. A valid batch with row diagnostics exits 0. Bad schema, invalid segments, unreadable files and malformed JSON exit 2 with no successful stdout. Never choose the first overlapping match, a nearby segment, or an invented target.

A clear, tested core earns full marks. Optional stretch: add one useful boundary test; no stretch is necessary. A web service, full framework, database, public deployment, or large architecture is outside the core scope.

Use these exact local verification runs after implementation; both valid fixture invocations should succeed and match the criteria above.

```sh
python3 app.py --input inputs/primary.json
python3 app.py --input inputs/secondary.json
```

## Time and AI use

Plan your own time within the 24-hour window. Prioritize the core contract and leave time for verification instead of adding features.

**AI is allowed and encouraged** for coding, explanation, test generation, critique and optional research. Tool choice is not graded. No AI tool is provided; you may use any AI tool you already have, and no purchase is required. Free/offline tools and completing the exercise without AI are supported. Check AI output against the rules, input rows and executed tests. Submit a short AI-use note with one concrete accepted, corrected or rejected output and how you checked it; if you did not use AI, state that. Do not invent an AI failure or share complete prompt histories, private account access, or secrets.

## Submission

Submit an archive or repository containing runnable source, tests, the supplied inputs, and:

1. A short run guide with exact commands for both fixtures and the meaningful checks; include representative outputs or assertions with input row/key references.
2. A concise decision/work log: priorities and what you deferred; one obstacle and response; one validation/refinement; known limits and next step. Cite fixture source IDs, event IDs, finding keys or row numbers as evidence.
3. The AI-use note described above.
4. A 3–5 minute walkthrough recording **or equivalent accessible text** explaining the core workflow, one edge case, and evidence of execution.

You do not need a public repository, deployment, PDF or proprietary tools. Document incomplete behavior honestly. Do not submit only a design or report: the runnable feature and reproducible tests are the primary deliverables.

Published scoring: **usable result 40, accuracy/verification 25, prioritization 20, communication/handoff 15**. Full marks are available on the core alone. Tool choice, AI-detector judgments, prose polish, hours worked and sheer output volume are not scored.
