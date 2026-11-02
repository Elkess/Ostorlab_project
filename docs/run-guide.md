# MapleLens Mapper run guide

Run these commands from:

`C:\Users\user\Desktop\Ostorlab_project\14-source-coordinate-mapper\14-source-coordinate-mapper`

## Environment and tests

```sh
python --version
python -m unittest discover -s tests -p '*_test.py' -v
```

The suite covers the C1–C5 contract, invalid input handling, exact path identity, overlap boundaries, both supplied fixtures, deterministic output and input immutability.

## Fixture runs

```sh
python app.py --input inputs\primary.json
python app.py --input inputs\secondary.json
```

Expected primary summary:

```json
{"ambiguous": 1, "input_rows": 12, "mapped": 7, "rejected_rows": 2, "unmapped": 2}
```

Expected secondary summary:

```json
{"ambiguous": 1, "input_rows": 12, "mapped": 6, "rejected_rows": 2, "unmapped": 3}
```

Representative primary evidence:

- `F01`, row 1, matches `M01`, maps to `src/start.py:10`.
- `F03`, row 3, is `unmapped` because generated line 4 is a gap.
- `F05`, row 5, is `ambiguous` with matches `M02` and `M03`.
- `F11` and `F12`, rows 11 and 12, are rejected because their generated lines are boolean and zero respectively.

Representative secondary refinement:

- `F04` changes from mapped through `M02` to unmapped because `M02` starts at generated line 6.
- `F01` and `F02` move within `M01` because its original start changes from 10 to 30.

## Fatal-input checks

```sh
python app.py --input inputs\malformed-input.txt
python app.py --input inputs\does-not-exist.json
```

Both commands must return exit code `2`, write a readable `error:` diagnostic to stderr, and write nothing to stdout. Valid batches return exit code `0`, including batches containing rejected finding rows.
