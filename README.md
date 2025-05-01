# uv Script Test Matrix

This script (`matrix.py`) provides a streamlined method for testing a Python script across a matrix of Python 3 versions. It serves as a focused utility for basic version compatibility validation, offering a less involved setup compared to comprehensive matrix testing frameworks such as tox or nox.  allows you to easily test another Python script against a matrix of different Python 3 versions using the `uv` package manager's powerful `uv run` functionality.

uv Script Test Matrix utilizes the `uv` package manager's `uv run` functionality and PEP 723 support to set up the necessary environment for each specified Python version, including installing the Python interpreter if need be, and runs your target script, reporting the results for each version.

## Prerequisites

* `uv` must be installed and available in your system's PATH. You can install `uv` from [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv). Additional installation methods and instructions can be found at [https://docs.astral.sh/uv/getting-started/installation/#installation-methods](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).

* An active internet connection is needed to install the script's dependencies, Python versions under test, and `uv Script Test Matrix`'s dependencies if they have not already been cached by `uv`.

## Installation and Running

This script uses `uv run` itself, which handles its own dependencies (`packaging`, `rich`). This means you don't need to manually install those libraries.

Simply run the script directly using `uvx`:

```bash
uv run matrix.py [OPTIONS] SCRIPT [SCRIPT_ARGS...]
```

## Usage

```text
uv run matrix.py [-h] [-v VERSION [VERSION ...]] [-r MIN_VERSION-MAX_VERSION] [-a ARG [ARG ...]] [-e ENV_FILE] [-l] [-t TIMEOUT] SCRIPT
```

### Arguments

#### Required Arguments

* `SCRIPT`: Path to the Python script you want to test against different Python versions. This path can be relative to your current directory

Plus one of the following options:

* `-v VERSION [VERSION ...]`, `--versions VERSION [VERSION ...]`:
    Specify one or more Python 3 versions to test against (e.g., `3.10`, `3.12`, `3.13`). This option cannot be used with `--range`.
* `-r MIN_VERSION-MAX_VERSION`, `--range MIN_VERSION-MAX_VERSION`:
    Specify a range of Python 3 versions to test against (e.g., `3.10-3.13`). The script will test all minor versions within this inclusive range (`3.10`, `3.11`, `3.12`, `3.13`).

Note that patch versions (e.g., `3.10.5`) are ignored; only the major and minor versions are used.

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

The script itself depends on `packaging` (for version parsing) and `rich` (for formatted output). These dependencies are automatically handled by `uv run` based on the `/// script` block of PEP 723 inline metadata in the script file.

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

Test a script `my_script.py` against Python 3.9 and 3.12:

```bash
uv run matrix.py -v 3.9 3.12 my_script.py
```

Test a script `another_script.py` against a range of Python versions (3.11, 3.12, 3.13), passing arguments `arg1` and `arg2`, loading environment variables from `.env` in the script's directory, and setting a 120-second timeout:

```bash
uv run matrix.py -r 3.11-3.13 -a arg1 arg2 -e .env -t 120 another_script.py
```

Test a script `test.py` against Python 3.8 with logging enabled:

```bash
uv run matrix.py -v 3.8 -l setup.py
```

## Notes

* Only Python 3.x is supported
* Only minor versions are considered (patch versions are ignored)
* Only CPython versions are supported at this time.

## License

The `uv Script Test Matrix` is licensed under the [MIT license](https://opensource.org/licenses/MIT). `uv` is licensed dually under [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0) and MIT license. Python is licensed under the [Python Software Foundation License 2](https://docs.python.org/3/license.html) and, since Python 3.8.6, the [Zero-Clause BSD License](https://docs.python.org/3/license.html#bsd0) with additional open source licenses for some stdlib code, all available at the PSF License page.
