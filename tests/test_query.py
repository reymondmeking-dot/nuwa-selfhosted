from __future__ import annotations

from pathlib import Path

import pytest

from nuwa_selfhosted.query import (
    QueryOptions,
    ensure_data,
    markdown,
    shortlist,
    wanted_tags_for,
)


def _catalog(tmp_path: Path) -> Path:
    root = tmp_path / "catalog"
    software = root / "software"
    software.mkdir(parents=True)
    (software / "ai.yml").write_text(
        """
name: AI Docker
description: A private assistant
tags:
  - Generative Artificial Intelligence (GenAI)
platforms: [Docker]
licenses: [MIT]
stargazers_count: 10
""".strip(),
        encoding="utf-8",
    )
    (software / "native.yml").write_text(
        """
name: AI Native
description: A local assistant
tags:
  - Generative Artificial Intelligence (GenAI)
platforms: [Python]
licenses: [MIT]
stargazers_count: 20
""".strip(),
        encoding="utf-8",
    )
    return root


def test_short_tag_alias_expands_to_catalog_tag() -> None:
    tags = wanted_tags_for("", ["ai"])

    assert "ai" in tags
    assert "Generative Artificial Intelligence (GenAI)" in tags


def test_docker_only_is_enforced_when_preference_is_disabled(tmp_path: Path) -> None:
    rows, errors, _ = shortlist(
        QueryOptions(
            data=str(_catalog(tmp_path)),
            tag=["ai"],
            docker_only=True,
            prefer_docker=False,
            no_update=True,
        )
    )

    assert errors == []
    assert [row["name"] for row in rows] == ["AI Docker"]


def test_non_checkout_data_directory_is_not_overwritten(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    (target / "keep.txt").write_text("user data", encoding="utf-8")

    with pytest.raises(SystemExit, match="refusing to overwrite"):
        ensure_data(target)

    assert (target / "keep.txt").read_text(encoding="utf-8") == "user data"


def test_markdown_escapes_catalog_cells() -> None:
    rendered = markdown(
        [
            {
                "name": "A|B",
                "description": "",
                "platforms": ["Docker|Linux"],
                "licenses": ["MIT"],
                "_score": 1,
                "_reasons": ["line\nbreak"],
            }
        ],
        [],
        [],
    )

    assert "A/B" in rendered
    assert "Docker/Linux" in rendered
    assert "line break" in rendered


def test_markdown_rejects_non_http_catalog_links() -> None:
    rendered = markdown(
        [
            {
                "name": "Unsafe",
                "website_url": "javascript:alert(1)",
                "source_code_url": "data:text/html,boom",
                "platforms": ["Docker"],
                "licenses": ["MIT"],
                "_score": 1,
                "_reasons": [],
            },
            {
                "name": "Safe",
                "website_url": "https://example.com/a_(b)",
                "source_code_url": "https://github.com/example/repo",
                "platforms": ["Docker"],
                "licenses": ["MIT"],
                "_score": 1,
                "_reasons": [],
            },
        ],
        [],
        [],
    )

    assert "javascript:" not in rendered
    assert "data:text" not in rendered
    assert "[Unsafe](" not in rendered
    assert "https://example.com/a_%28b%29" in rendered
    assert "[source](https://github.com/example/repo)" in rendered
