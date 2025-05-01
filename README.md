# uv Script Test Matrix

This script (`test-matrix.py`) allows you to easily test another Python script against a matrix of different Python 3 versions using the `uv` package manager's powerful `uv run --script` functionality.

It sets up the necessary environment for each specified Python version and runs your target script, reporting the results for each version.

## Prerequisites

* `uv` must be installed and available in your system's PATH. You can install `uv` from [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv). Additional installation methods and instructions can be found at [https://docs.astral.sh/uv/getting-started/installation/#installation-methods](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).

## Installation and Running

This script uses `uv run --script` itself, which handles its own dependencies (`packaging`, `rich`). This means you don't need to manually install those libraries.

Simply run the script directly using `uv run`:

```bash
uv run matrix [OPTIONS] SCRIPT [SCRIPT_ARGS...]
```

or

```bash
uv run test-matrix.py [OPTIONS] SCRIPT [SCRIPT_ARGS...]
```

## Usage

```text
uv run matrix [-h] [-v VERSION [VERSION ...]] [-r MIN_VERSION-MAX_VERSION] [-a ARG [ARG ...]] [-e ENV_FILE] [-l] [-t TIMEOUT] SCRIPT
```

### Arguments

#### Required Arguments

* `SCRIPT`: Path to the Python script you want to test against different Python versions. This path can be relative to your current directory

Plus one of the following options:

* `-v VERSION [VERSION ...]`, `--versions VERSION [VERSION ...]`:
    Specify one or more exact Python 3 versions to test against (e.g., `3.10`, `3.12.1`, `3.13`). This option cannot be used with `--range`.
* `-r MIN_VERSION-MAX_VERSION`, `--range MIN_VERSION-MAX_VERSION`:
    Specify a range of Python 3 minor versions to test against (e.g., `3.10-3.13`). The script will test all minor versions within this inclusive range (`3.10`, `3.11`, `3.12`, `3.13`). Note that patch versions (e.g., `3.10.5-3.13.0`) are ignored for the range calculation; only the major and minor versions determine the range boundaries.

#### Optional Arguments

* `-a ARG [ARG ...]`, `--args ARG [ARG ...]`:
    Arguments to pass to the script being tested (`SCRIPT`).
* `-e ENV_FILE`, `--env ENV_FILE`:
    Path to an env (`.env`) file. Environment variables from this file will be loaded for the script being tested. This path should be either **absolute** or **relative to the directory of the script being tested**.
* `-l`, `--logging`:
    Enable logging the detailed output of each test run to a file. The log file will be named `<SCRIPT_NAME>.log` and placed in the same directory as the script being tested.
* `-t TIMEOUT`, `--timeout TIMEOUT`:
    Set a timeout in seconds for each individual test run with a specific Python version. If a test run exceeds this duration, it will be considered a failure. Defaults to 60 seconds.

## How it Works

The script iterates through the specified Python versions. For each version, it constructs and executes a command using `uv run --python=<version> ...`. The working directory for the `uv run` subprocess is set to the directory containing the script being tested, allowing the target script to be found and run correctly. The exit code of the `uv run` command determines if the test for that version passed (exit code 0) or failed (non-zero exit code or timeout).

## Dependencies

The script itself depends on `packaging` (for version parsing) and `rich` (for formatted output). These dependencies are automatically handled by `uv run --script` based on the `/// script` block in the script file.

## Output

Upon completion, the script prints a formatted table using `rich` showing each tested Python version and whether the script passed or failed for that version.

```text
Test Matrix Results:
|---------|--------|
| Python  | Result |
|---------|--------|
| 3.9     | PASS   |
| 3.10    | PASS   |
| 3.11    | FAIL   |
|---------|--------|
```

If logging is enabled with `-l`, the full standard output and standard error of each test run are written to a `.log` file next to the script being tested.

## Examples

Test a script `my_script.py` against Python 3.9, 3.10, and 3.12:

```bash
uv run test-matrix.py -v 3.9 3.10 3.12 my_script.py
```

Test a script `another_script.py` against a range of Python versions (3.11, 3.12, 3.13), passing arguments `arg1` and `arg2`, loading environment variables from `.env` in the script's directory, and setting a 120-second timeout:

```bash
uv run test-matrix.py -r 3.11-3.13 -a arg1 arg2 -e .env -t 120 another_script.py
```

Test a script `setup.py` against Python 3.8 with logging enabled:

```bash
uv run --script test-matrix.py -v 3.8 -l setup.py
```

## Notes

* Only Python 3.x is supported
* When using --range, only minor versions are considered (patch versions are ignored)
* For testing with specific patch versions (e.g., 3.10.2), use the --versions option
