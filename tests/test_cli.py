from __future__ import annotations

import pytest

from nuwa_selfhosted.cli import build_parser


def test_limit_must_be_positive() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["query", "wiki", "--limit", "0"])
