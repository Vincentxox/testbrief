"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import List, Optional

from testbrief import __version__
from testbrief.parsers import PARSERS
from testbrief.render import RENDERERS

EXIT_OK = 0
EXIT_TEST_FAILURES = 1
EXIT_BAD_INPUT = 2

_EXTENSION_FORMATS = {".xml": "junit", ".json": "newman"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="testbrief",
        description="Summarize test reports (JUnit XML, Newman JSON) as Markdown.",
    )
    parser.add_argument("files", nargs="+", help="report files to summarize")
    parser.add_argument(
        "-f",
        "--format",
        choices=["auto", *PARSERS],
        default="auto",
        help="input format (default: detect from the file extension)",
    )
    parser.add_argument(
        "-o", "--output", help="write the summary to this file instead of stdout"
    )
    parser.add_argument(
        "--slowest",
        type=int,
        default=5,
        metavar="N",
        help="list the N slowest tests when the report has timings (default: 5)",
    )
    parser.add_argument(
        "--fail-on-failures",
        action="store_true",
        help=f"exit with code {EXIT_TEST_FAILURES} when any test failed or errored",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def detect_format(path: str, forced: str) -> str:
    if forced != "auto":
        return forced
    extension = os.path.splitext(path)[1].lower()
    if extension not in _EXTENSION_FORMATS:
        raise ValueError(
            f"{path}: cannot detect the format from the extension, use --format"
        )
    return _EXTENSION_FORMATS[extension]


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    reports = []
    for path in args.files:
        try:
            parser_name = detect_format(path, args.format)
            reports.append(PARSERS[parser_name](path))
        except (OSError, ValueError, ET.ParseError, json.JSONDecodeError) as error:
            print(f"testbrief: error: {error}", file=sys.stderr)
            return EXIT_BAD_INPUT

    output = RENDERERS["md"](reports, top_slowest=args.slowest)

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(output)
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(output)

    if args.fail_on_failures and any(r.has_failures for r in reports):
        return EXIT_TEST_FAILURES
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
