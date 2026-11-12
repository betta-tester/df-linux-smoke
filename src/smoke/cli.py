"""Command line entry point for ``smoke``."""

import argparse
import sys
from collections.abc import Sequence
from importlib.metadata import version


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
    sys.stdout.write(f"smoke {version('smoke')}\n")
    return 0
