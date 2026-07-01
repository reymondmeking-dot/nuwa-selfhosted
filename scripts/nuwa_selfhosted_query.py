#!/usr/bin/env python3
"""Backward-compatible shim.

Previously this file held the full query implementation. It has been moved
into the ``nuwa_selfhosted`` package (``src/nuwa_selfhosted/``) and exposed
via the ``nuwa-selfhosted`` console script.

This shim keeps ``python scripts/nuwa_selfhosted_query.py "..."`` working by
forwarding to ``nuwa-selfhosted query ...``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running directly from a source checkout without installing.
_HERE = Path(__file__).resolve().parent
_SRC = _HERE.parent / "src"
if _SRC.is_dir():
    sys.path.insert(0, str(_SRC))

try:
    from nuwa_selfhosted.cli import main as _cli_main
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Could not import nuwa_selfhosted. Install with: pip install -e ."
    ) from exc


def main() -> int:
    argv = list(sys.argv[1:])
    # If the user did not already pick a subcommand, assume "query" so the
    # old positional-query invocation keeps working.
    known_subcommands = {"query", "update", "version"}
    if not argv or (argv[0] not in known_subcommands and not argv[0].startswith("-")):
        argv = ["query", *argv]
    elif argv and argv[0].startswith("-") and "query" not in argv:
        argv = ["query", *argv]
    return _cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
