"""Core query logic for awesome-selfhosted-data.

This module is intentionally privacy-neutral: it does not know about any
user's servers, credentials, domains, or local environment. It only reads
the public awesome-selfhosted-data YAML catalog.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, urlparse

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Install with: pip install pyyaml (or `pip install nuwa-selfhosted`)"
    ) from exc

DATA_REPO = "https://github.com/awesome-selfhosted/awesome-selfhosted-data.git"
DEFAULT_DATA_PATH = os.environ.get(
    "NUWA_SELFHOSTED_DATA", "data/awesome-selfhosted-data"
)

TAG_HINTS: dict[str, list[str]] = {
    "notion": ["Knowledge Management Tools", "Note-taking & Editors", "Wikis"],
    "knowledge": ["Knowledge Management Tools", "Wikis", "Note-taking & Editors"],
    "wiki": ["Wikis", "Knowledge Management Tools"],
    "notes": ["Note-taking & Editors", "Knowledge Management Tools"],
    "zapier": ["Automation", "Software Development - Low Code"],
    "make": ["Automation", "Software Development - Low Code"],
    "automation": ["Automation"],
    "analytics": ["Analytics"],
    "ga": ["Analytics"],
    "crm": ["Customer Relationship Management (CRM)"],
    "file": [
        "File Transfer & Synchronization",
        "File Transfer - Single-click & Drag-n-drop Upload",
        "File Transfer - Object Storage & File Servers",
    ],
    "storage": [
        "File Transfer - Object Storage & File Servers",
        "File Transfer & Synchronization",
    ],
    "s3": ["File Transfer - Object Storage & File Servers"],
    "video": ["Media Streaming - Video Streaming", "Media Management"],
    "media": ["Media Management", "Media Streaming - Multimedia Streaming"],
    "youtube": ["Media Streaming - Video Streaming"],
    "project": [
        "Software Development - Project Management",
        "Task Management & To-do Lists",
        "Ticketing",
    ],
    "trello": [
        "Task Management & To-do Lists",
        "Software Development - Project Management",
    ],
    "jira": ["Software Development - Project Management", "Ticketing"],
    "ai": ["Generative Artificial Intelligence (GenAI)"],
    "llm": ["Generative Artificial Intelligence (GenAI)"],
    "rag": [
        "Generative Artificial Intelligence (GenAI)",
        "Knowledge Management Tools",
    ],
    "chatgpt": ["Generative Artificial Intelligence (GenAI)"],
    "monitoring": ["Monitoring & Status Pages"],
    "status": ["Monitoring & Status Pages"],
    "password": ["Password Managers"],
    "bookmark": ["Bookmarks and Link Sharing"],
    "rss": ["Feed Readers"],
    "feed": ["Feed Readers"],
    "cms": ["Content Management Systems (CMS)"],
    "ecommerce": ["E-commerce"],
    "shop": ["E-commerce"],
}


@dataclass
class QueryOptions:
    """Options for a shortlist query."""

    query: str = ""
    data: str = DEFAULT_DATA_PATH
    limit: int = 8
    tag: list[str] = field(default_factory=list)
    prefer_docker: bool = True
    docker_only: bool = False
    include_proprietary: bool = False
    include_archived: bool = False
    no_update: bool = False


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def ensure_data(path: Path, update: bool = True) -> Path:
    """Ensure awesome-selfhosted-data is available at ``path``.

    Clones the repo when missing; runs ``git pull --ff-only`` when present
    unless ``update`` is False.
    """
    if (path / "software").is_dir():
        if update and (path / ".git").is_dir():
            try:
                _run(["git", "pull", "--ff-only"], cwd=path)
            except Exception as exc:
                print(f"Warning: could not update data repo: {exc}", file=sys.stderr)
        return path

    if path.exists():
        if not path.is_dir():
            raise SystemExit(f"Data path exists but is not a directory: {path}")
        if any(path.iterdir()):
            raise SystemExit(
                f"{path} exists but is not an awesome-selfhosted-data checkout; "
                "refusing to overwrite it. Choose another --data path."
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", "--depth", "1", DATA_REPO, str(path)])
    return path


def load_items(data_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    software_dir = data_path / "software"
    if not software_dir.is_dir():
        raise SystemExit(f"Missing software directory: {software_dir}")
    items: list[dict[str, Any]] = []
    errors: list[str] = []
    for file in sorted(software_dir.glob("*.yml")):
        try:
            entry = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
            entry["_file"] = file.name
            items.append(entry)
        except Exception as exc:
            errors.append(f"{file.name}: {exc}")
    return items, errors


def normalize_words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9+#.\-]+", text.lower())


def infer_tags(query: str) -> set[str]:
    words = normalize_words(query)
    tags: set[str] = set()
    for word in words:
        tags.update(TAG_HINTS.get(word, []))
    return tags


def wanted_tags_for(query: str, explicit_tags: Iterable[str]) -> set[str]:
    """Expand short tag aliases while preserving exact catalog tag names."""
    tags = infer_tags(query)
    for tag in explicit_tags:
        cleaned = str(tag).strip()
        if not cleaned:
            continue
        tags.add(cleaned)
        tags.update(infer_tags(cleaned))
    return tags


def entry_text(entry: dict[str, Any]) -> str:
    parts = [entry.get("name", ""), entry.get("description", "")]
    parts.extend(entry.get("tags") or [])
    parts.extend(entry.get("platforms") or [])
    return " ".join(str(x) for x in parts).lower()


def maintenance_bonus(entry: dict[str, Any]) -> int:
    bonus = 0
    if entry.get("current_release"):
        bonus += 6
    if entry.get("updated_at"):
        bonus += 6
    if entry.get("commit_history"):
        bonus += 3
    return min(bonus, 15)


def stars_bonus(entry: dict[str, Any]) -> int:
    stars = entry.get("stargazers_count")
    if not isinstance(stars, int) or stars <= 0:
        return 0
    return min(10, int(math.log10(stars + 1) * 2.5))


def score_entry(
    entry: dict[str, Any],
    query_words: list[str],
    wanted_tags: set[str],
    prefer_docker: bool,
) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    tags = set(entry.get("tags") or [])
    platforms = set(entry.get("platforms") or [])
    text = entry_text(entry)

    tag_hits = tags & wanted_tags
    if tag_hits:
        score += 30 + min(15, 5 * len(tag_hits))
        reasons.append("tag: " + ", ".join(sorted(tag_hits)[:3]))

    keyword_hits = [w for w in query_words if len(w) > 1 and w in text]
    if keyword_hits:
        score += min(30, 8 * len(set(keyword_hits)))
        reasons.append("keywords: " + ", ".join(sorted(set(keyword_hits))[:4]))

    if "Docker" in platforms:
        score += 15 if prefer_docker else 8
        reasons.append("Docker")
    elif prefer_docker:
        score -= 8

    mb = maintenance_bonus(entry)
    if mb:
        score += mb
        reasons.append("maintenance metadata")

    sb = stars_bonus(entry)
    if sb:
        score += sb

    if entry.get("demo_url"):
        score += 5
        reasons.append("demo")

    if entry.get("depends_3rdparty"):
        score -= 5
        reasons.append("depends on third-party service")

    return score, reasons


def difficulty(entry: dict[str, Any]) -> str:
    platforms = set(entry.get("platforms") or [])
    if "K8S" in platforms and "Docker" not in platforms:
        return "High"
    if "Docker" in platforms:
        return "Low-Medium"
    if platforms & {"PHP", "Nodejs", "Python", "Java", "Ruby"}:
        return "Medium"
    return "Unknown"


def caution(entry: dict[str, Any]) -> str:
    notes: list[str] = []
    licenses = set(entry.get("licenses") or [])
    if "⊘ Proprietary" in licenses:
        notes.append("proprietary")
    if any(str(x).startswith("AGPL") for x in licenses):
        notes.append("AGPL obligations")
    if any(str(x).startswith("GPL") for x in licenses):
        notes.append("GPL obligations")
    if entry.get("depends_3rdparty"):
        notes.append("third-party dependency")
    if entry.get("archived"):
        notes.append("archived")
    return "; ".join(notes) if notes else "-"


def shortlist(
    options: QueryOptions,
) -> tuple[list[dict[str, Any]], list[str], set[str]]:
    data = ensure_data(Path(options.data), update=not options.no_update)
    items, errors = load_items(data)
    query_words = normalize_words(options.query)
    wanted_tags = wanted_tags_for(options.query, options.tag or [])

    rows: list[dict[str, Any]] = []
    for entry in items:
        licenses = set(entry.get("licenses") or [])
        if not options.include_proprietary and "⊘ Proprietary" in licenses:
            continue
        if not options.include_archived and entry.get("archived"):
            continue
        if options.docker_only and "Docker" not in set(entry.get("platforms") or []):
            continue
        score, reasons = score_entry(
            entry, query_words, wanted_tags, options.prefer_docker
        )
        if score <= 0 and (wanted_tags or query_words):
            continue
        entry = dict(entry)
        entry["_score"] = score
        entry["_reasons"] = reasons
        rows.append(entry)

    rows.sort(
        key=lambda e: (e.get("_score", 0), e.get("stargazers_count") or 0),
        reverse=True,
    )
    return rows[: max(0, options.limit)], errors, wanted_tags


def _markdown_cell(value: Any) -> str:
    """Escape catalog text so one malformed value cannot break the table."""
    return str(value or "").replace("\r", " ").replace("\n", " ").replace("|", "/")


def _safe_markdown_url(value: Any) -> str:
    """Return an escaped public web URL, or an empty string for unsafe schemes."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlparse(raw)
        hostname = parsed.hostname
    except ValueError:
        return ""
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        return ""
    return quote(raw, safe=":/?#[]@!$&'*+,;=%~-._")


def markdown(
    rows: list[dict[str, Any]], errors: list[str], wanted_tags: Iterable[str]
) -> str:
    out: list[str] = []
    wanted_tags = list(wanted_tags)
    out.append(
        f"Matched tags: {', '.join(sorted(wanted_tags)) if wanted_tags else '(keyword only)'}"
    )
    if errors:
        out.append(f"YAML parse warnings: {len(errors)}")
    out.append("")
    out.append(
        "| Rank | Project | Score | Why | Platform | License | Source | Difficulty | Cautions |"
    )
    out.append("|---:|---|---:|---|---|---|---|---|---|")
    for i, e in enumerate(rows, 1):
        name = _markdown_cell(e.get("name", "")).replace("]", "\\]")
        website = _safe_markdown_url(e.get("website_url", ""))
        project = (
            f"[{name}]({website})"
            if website
            else name
        )
        source = _safe_markdown_url(e.get("source_code_url") or "")
        if source:
            source = f"[source]({source})"
        out.append(
            "| {rank} | {project} | {score} | {why} | {platform} | {license} | {source} | {difficulty} | {caution} |".format(
                rank=i,
                project=project,
                score=e.get("_score", 0),
                why=_markdown_cell(", ".join(e.get("_reasons") or [])[:90]),
                platform=_markdown_cell(", ".join(e.get("platforms") or [])),
                license=_markdown_cell(", ".join(e.get("licenses") or [])),
                source=source,
                difficulty=difficulty(e),
                caution=caution(e).replace("|", "/"),
            )
        )
    return "\n".join(out)


def as_json(
    rows: list[dict[str, Any]], errors: list[str], wanted_tags: Iterable[str]
) -> str:
    return json.dumps(
        {
            "matched_tags": sorted(list(wanted_tags)),
            "errors": errors,
            "results": rows,
        },
        ensure_ascii=False,
        indent=2,
    )


def update_data(data_path: str | None = None) -> Path:
    """Force re-clone / update the awesome-selfhosted-data checkout."""
    path = Path(data_path or DEFAULT_DATA_PATH)
    if path.exists() and (path / ".git").is_dir():
        _run(["git", "pull", "--ff-only"], cwd=path)
        return path
    # Fresh clone (parent must exist)
    if path.exists() and not (path / ".git").is_dir():
        raise SystemExit(
            f"{path} exists but is not a git checkout; refusing to overwrite."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", "--depth", "1", DATA_REPO, str(path)])
    return path
