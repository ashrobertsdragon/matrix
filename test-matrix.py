#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "packaging",
#     "rich",
# ]
# ///
"""
Test a script against multiple Python versions using uv.

Usage:
    test-matrix.py [-h] [-v VERSION] [-r MIN_VERSION-MAX_VERSION] SCRIPT [SCRIPT_ARGS...] [--env ENV_FILE] [--logging]
"""

import argparse
import shlex
import subprocess
import sys
import warnings
from pathlib import Path

from packaging.version import Version, InvalidVersion
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def validate_version(v: str) -> Version | None:
    """
    Validate a version string.

    Args:
        v (str): The version string to validate.

    Returns:
        Version: The validated version string if valid, None otherwise.
    """
    try:
        version = Version(v)
        if version.major != 3:
            raise ValueError(f"Warning: Only Python 3 is supported (got {v})")
        return version
    except InvalidVersion:
        warnings.warn(f"Warning: Invalid version string: {v}", RuntimeWarning)
        return None


def resolve_versions(versions: list[str]) -> list[str]:
    """
    Resolve a list of versions to test against.

    Args:
        versions (list[str]): A list of version strings.

    Returns:
        list[str]: A list of resolved version strings.
    """
    if "-" not in versions[0]:
        print(len(versions))
        return [v for v in versions if validate_version(v)]

    if len(versions) != 1:
        raise ValueError("Range mode only supports one argument")

    min_version_str, max_version_str = versions[0].split("-")
    min_version = validate_version(min_version_str)
    max_version = validate_version(max_version_str)

    if not min_version or not max_version:
        return []

    if min_version.micro != 0 or max_version.micro != 0:
        warnings.warn(
            "Warning: Patch versions will be ignored in range mode. "
            "Only minor versions are used.\n"
            "To use patch versions, specify versions individually"
        )

    return [
        f"3.{minor}"
        for minor in range(min_version.minor, max_version.minor + 1)
    ]


def sanitize_args(args: list[str]) -> list[str]:
    """
    Sanitize a list of arguments."""
    return [shlex.quote(arg) for arg in args]


def output(message: str, logging: bool, log_file: Path) -> None:
    """
    Log or print a message.

    Args:
        message (str): The message to log or print.
        logging (bool): Whether to log the message.
        log_file (Path): The file to log the message to if logging is True.
    """
    if logging:
        with log_file.open("a") as f:
            f.write(f"{message}\n")
    else:
        console.print(message)


def run_version(
    python_version: str,
    script: Path,
    logging: bool,
    log_file: Path,
    timeout: int,
    script_args: list[str] | None = None,
    env_file: str | None = None,
) -> tuple[str, bool]:
    """
    Run a script using uv with a specific Python version.

    Args:
        python_version (str): The Python version to run the script with.
        script (Path): The path to the script to run.
        logging (bool): Whether to log the output of the script.
        log_file (Path): The file to log the output to.
        script_args (list[str], optional): The arguments to pass to the
            script. Defaults to None.
        env_file (str, optional): The path to the env file to use. Defaults
            to None.
        timeout int: The timeout in seconds..

    Returns:
        tuple[str, bool]: The Python version and whether the script passed or
            failed.
    """
    if script_args is None:
        script_args = []

    script_file = str(script.name)
    script_dir = str(script.resolve().parent)

    args = [
        "uv",
        "run",
        f"--python={python_version}",
    ]
    if env_file:
        args.extend(["--env-file", env_file])

    args.append(script_file)
    script_args = sanitize_args(script_args)
    args.extend(script_args)

    start_message = f"Testing with Python {python_version}..."
    output(start_message, logging, log_file)

    output(f"with {args}", logging, log_file)

    try:
        result = subprocess.run(
            args,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
        output(result.stdout, logging, log_file)
        return (python_version, result.returncode == 0)
    except BaseException as e:
        message = f"Failed to run: {e}"
        output(message, logging, log_file)
        return (python_version, False)


def print_results(results: list[tuple[str, bool]]) -> None:
    """Print the results of the test matrix."""

    console.print("\n[bold underline]Test Matrix Results:[/bold underline]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Python")
    table.add_column("Result")

    for version, success in results:
        result_text = Text("PASS" if success else "FAIL")
        result_text.stylize("green" if success else "red")
        table.add_row(version, result_text)

    console.print(table)


def range_in_list(range: str) -> list[str]:
    return [range]


def create_parser() -> argparse.Namespace:
    """Create an argument parser."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "script",
        help="Path to script to test against (Relative path ok)",
        type=Path,
    )
    versions_group = parser.add_mutually_exclusive_group(required=True)
    versions_group.add_argument(
        "-v",
        "--versions",
        help=(
            "Python versions to test against "
            "as individual Python 3.x or 3.x.x versions (e.g. 3.10 3.13.2). "
            "Note: Cannot be used with --range."
        ),
        metavar="VERSION",
        nargs="+",
    )
    versions_group.add_argument(
        "-r",
        "--range",
        help=(
            "Python versions to test against as a range of Python 3.x "
            "versions (e.g. 3.10-3.13). Note: Cannot be used with --versions."
        ),
        metavar="MIN_VERSION-MAX_VERSION",
        dest="versions",
        type=range_in_list,
    )
    parser.add_argument(
        "-a",
        "--args",
        help="Arguments to pass to script",
        nargs="+",
        metavar="ARG",
        dest="script_args",
    )
    parser.add_argument(
        "-e",
        "--env",
        help="Path to env (.env) file (Path relative to script location ok)",
    )
    parser.add_argument(
        "-t", "--timeout", help="Timeout in seconds", default=60, type=int
    )
    parser.add_argument(
        "-l", "--logging", action="store_true", help="Enable logging to file"
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def main() -> None:
    args: argparse.Namespace = create_parser()

    versions: list[str] = resolve_versions(args.versions)
    if not versions:
        raise ValueError("No valid Python versions found to test against.")

    script_path: Path = args.script
    if not script_path.is_file():
        raise ValueError("Script not found.")
    if script_path.suffix != ".py":
        raise ValueError("Script must be a Python file.")

    log_file: Path = script_path.with_suffix(".log")

    if (
        args.env
        and not Path(args.env).exists()
        and not (script_path / args.env).exists()
    ):
        raise ValueError("Env file not found.")
    results = [
        run_version(
            python_version=version,
            script=script_path,
            logging=args.logging,
            log_file=log_file,
            timeout=args.timeout,
            script_args=args.script_args,
            env_file=args.env,
        )
        for version in versions
    ]

    print_results(results)


if __name__ == "__main__":
    main()
