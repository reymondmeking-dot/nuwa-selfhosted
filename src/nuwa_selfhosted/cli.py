"""Command-line interface for ``nuwa-selfhosted``.

Subcommands:

* ``query``   — search awesome-selfhosted-data and print a shortlist.
* ``update``  — (re-)clone / update the local awesome-selfhosted-data checkout.
* ``version`` — print the package version.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Sequence

from . import __version__
from .query import (
    DEFAULT_DATA_PATH,
    QueryOptions,
    as_json,
    markdown,
    shortlist,
    update_data,
)


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def _add_query_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "query",
        help="Query awesome-selfhosted-data for self-hosted software candidates.",
    )
    p.add_argument(
        "query",
        nargs="?",
        default="",
        help="Natural language need, e.g. 'notion knowledge base' or 'zapier automation'.",
    )
    p.add_argument(
        "--data",
        default=DEFAULT_DATA_PATH,
        help="Path to awesome-selfhosted-data checkout (env: NUWA_SELFHOSTED_DATA).",
    )
    p.add_argument("--limit", type=_positive_int, default=8)
    p.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Force one or more awesome-selfhosted tags (repeatable).",
    )
    p.add_argument(
        "--prefer-docker",
        action="store_true",
        default=True,
        help="Boost Docker projects. Enabled by default.",
    )
    p.add_argument(
        "--no-prefer-docker", action="store_false", dest="prefer_docker"
    )
    p.add_argument(
        "--docker-only",
        action="store_true",
        help="Only return Docker projects.",
    )
    p.add_argument(
        "--include-proprietary",
        action="store_true",
        help="Allow entries licensed as proprietary.",
    )
    p.add_argument(
        "--include-archived",
        action="store_true",
        help="Allow archived entries.",
    )
    p.add_argument(
        "--no-update",
        action="store_true",
        help="Do not git pull an existing data checkout.",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit JSON instead of Markdown.",
    )
    p.set_defaults(func=_cmd_query)


def _add_update_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "update",
        help="Clone or update the local awesome-selfhosted-data checkout.",
    )
    p.add_argument(
        "--data",
        default=DEFAULT_DATA_PATH,
        help="Path to the checkout (env: NUWA_SELFHOSTED_DATA).",
    )
    p.set_defaults(func=_cmd_update)


def _add_version_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("version", help="Print the nuwa-selfhosted version.")
    p.set_defaults(func=_cmd_version)


def _cmd_query(args: argparse.Namespace) -> int:
    options = QueryOptions(
        query=args.query or "",
        data=args.data,
        limit=args.limit,
        tag=list(args.tag or []),
        prefer_docker=args.prefer_docker,
        docker_only=args.docker_only,
        include_proprietary=args.include_proprietary,
        include_archived=args.include_archived,
        no_update=args.no_update,
    )
    if not options.query and not options.tag:
        print(
            "Provide a query string or at least one --tag. Example:\n"
            "  nuwa-selfhosted query 'notion knowledge base' --limit 5",
            file=sys.stderr,
        )
        return 2
    rows, errors, wanted_tags = shortlist(options)
    if args.as_json:
        print(as_json(rows, errors, wanted_tags))
    else:
        print(markdown(rows, errors, wanted_tags))
    return 0


def _cmd_update(args: argparse.Namespace) -> int:
    path = update_data(args.data)
    print(f"awesome-selfhosted-data ready at: {path}")
    return 0


def _cmd_version(_args: argparse.Namespace) -> int:
    print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nuwa-selfhosted",
        description="Query awesome-selfhosted-data and return practical shortlists.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"nuwa-selfhosted {__version__}",
    )
    sub = parser.add_subparsers(dest="command", metavar="{query,update,version}")
    _add_query_parser(sub)
    _add_update_parser(sub)
    _add_version_parser(sub)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    try:
        return int(args.func(args) or 0)
    except FileNotFoundError as exc:
        missing = exc.filename or "required executable"
        print(f"Error: {missing} was not found on PATH.", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        command = " ".join(str(part) for part in exc.cmd)
        print(
            f"Error: command failed with exit {exc.returncode}: {command}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
