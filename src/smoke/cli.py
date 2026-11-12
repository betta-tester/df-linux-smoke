"""Command line entry point for ``smoke``."""

import argparse
import sys
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version

NOT_INSTALLED_MESSAGE = (
    "smoke: distribution 'smoke' is not installed in this environment; "
    "create it with `uv sync`\n"
)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser; ``--version`` is a plain flag."""
    parser = argparse.ArgumentParser(prog="smoke")
    parser.add_argument("--version", action="store_true", help="print version")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``smoke`` command and return its exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.version:
        parser.print_usage(sys.stderr)
        return 2
    try:
        installed = version("smoke")
    except PackageNotFoundError:
        sys.stderr.write(NOT_INSTALLED_MESSAGE)
        return 1
    sys.stdout.write(f"smoke {installed}\n")
    return 0
