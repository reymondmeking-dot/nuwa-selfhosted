# Nuwa Selfhosted

Nuwa Selfhosted is a Hermes Agent skill for finding, comparing, and planning deployments of self-hosted software using the public [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) ecosystem.

It is designed for practical software selection:

- Find open-source or self-hosted alternatives to SaaS tools.
- Prefer Docker-friendly options for VPS or personal servers.
- Filter out proprietary or archived entries by default.
- Show licenses, source URLs, deployment difficulty, and cautions.
- Keep the catalog fresh by reading `awesome-selfhosted-data` dynamically instead of embedding a stale list.

## What it uses

Primary machine-readable data source:

```text
https://github.com/awesome-selfhosted/awesome-selfhosted-data
```

Human-readable catalog:

```text
https://awesome-selfhosted.net/
https://github.com/awesome-selfhosted/awesome-selfhosted
```

## Files

```text
SKILL.md                              Hermes skill instructions
scripts/nuwa_selfhosted_query.py      Optional CLI helper for querying the catalog
README.md                             This introduction
LICENSE                               MIT license
.gitignore                            Keeps caches and private files out of git
```

## Privacy

This repository intentionally contains no private server information, credentials, domains, phone numbers, IP addresses, SSH paths, or API keys.

Public examples use placeholders only:

```text
example.com
YOUR_SERVER_IP
/path/to/app
<token>
```

## Install in Hermes

Install directly from GitHub:

```bash
hermes skills install https://raw.githubusercontent.com/reymondmeking-dot/nuwa-selfhosted/main/SKILL.md
```

From a local checkout:

```bash
hermes skills install ./SKILL.md
```

Or copy this folder into your Hermes skills directory as `nuwa-selfhosted`.

## Use the helper script directly

The script can clone/update `awesome-selfhosted-data` into `data/awesome-selfhosted-data` automatically:

```bash
python scripts/nuwa_selfhosted_query.py "notion knowledge base" --limit 8
python scripts/nuwa_selfhosted_query.py "zapier automation" --limit 8
python scripts/nuwa_selfhosted_query.py "ai chat rag" --tag "Generative Artificial Intelligence (GenAI)" --json
```

Use an existing data checkout:

```bash
python scripts/nuwa_selfhosted_query.py "analytics" --data /path/to/awesome-selfhosted-data --limit 10
```

Return Docker-only candidates:

```bash
python scripts/nuwa_selfhosted_query.py "file storage" --docker-only --limit 10
```

Include proprietary entries only when you explicitly want commercial/closed-source options:

```bash
python scripts/nuwa_selfhosted_query.py "self hosting panel" --include-proprietary
```

## Typical output

The helper returns a Markdown table with:

- Project and website URL
- Score and match reason
- Platform
- License
- Source URL
- Deployment difficulty
- Cautions such as AGPL/GPL obligations or proprietary license

## Recommended workflow

1. Ask for a self-hosted alternative or category.
2. Query the catalog and return 3-8 strong candidates.
3. Let the user select one.
4. Inspect the selected project's official repository and deployment docs.
5. Only then produce Docker Compose, reverse proxy, HTTPS, backup, and health-check instructions.

## License

MIT
