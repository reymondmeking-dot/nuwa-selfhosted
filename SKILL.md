---
name: nuwa-selfhosted
description: Use when finding, comparing, or planning deployment of self-hosted software from awesome-selfhosted. Dynamically reads awesome-selfhosted-data, filters by need, license, platform, and maintenance signals, then returns a practical shortlist with deployment cautions.
version: 1.1.1
author: ReyMao
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [self-hosted, devops, docker, awesome-selfhosted, software-selection, deployment]
    related_skills: [remote-server-deployment, github-repo-management]
---

# Nuwa Selfhosted

## Overview

Nuwa Selfhosted is a selection workflow for choosing self-hosted applications from the community-maintained awesome-selfhosted catalog. It turns a user request like “find me a self-hosted Notion alternative” or “recommend an open-source Zapier replacement I can run with Docker” into a grounded shortlist backed by the machine-readable `awesome-selfhosted-data` repository.

The skill does **not** embed the full catalog. The list is too large and changes too often. Instead, update or clone the data repository, parse `software/*.yml`, filter candidates, and explain tradeoffs in a format the user can act on.

Primary data source:

```text
https://github.com/awesome-selfhosted/awesome-selfhosted-data
```

Human-readable catalog:

```text
https://awesome-selfhosted.net/
https://github.com/awesome-selfhosted/awesome-selfhosted
```

## When to Use

Use this skill when the user asks for:

- A self-hosted, open-source, or private-deployment alternative to a SaaS product.
- Software recommendations by category, for example knowledge base, CRM, analytics, file sharing, automation, AI chat, monitoring, media streaming, project management, wiki, or document management.
- Docker-first options for a personal VPS, home server, NAS, or company server.
- A comparison between several self-hosted projects.
- A shortlist before deployment planning.
- A reusable way to query awesome-selfhosted data.

Do **not** use this skill as the final authority for deployment commands. After the user selects a project, inspect that project’s official documentation and repository before writing Docker Compose, nginx, database, upgrade, or backup instructions.

## Privacy Rule

Never include private user environment details in reusable output, public repositories, or generated skill files. Do not publish server IPs, passwords, API keys, personal phone numbers, private domains, local usernames, `.env` contents, SSH details, or credential paths.

For public examples, use placeholders:

```text
example.com
YOUR_SERVER_IP
/path/to/app
<token>
```

## Data Workflow

1. **Prepare the data cache.** Use an existing checkout if available; otherwise clone the data repository into a neutral project cache directory.

   ```bash
   mkdir -p data
   if [ -d data/awesome-selfhosted-data/.git ]; then
     git -C data/awesome-selfhosted-data pull --ff-only
   else
     git clone --depth 1 https://github.com/awesome-selfhosted/awesome-selfhosted-data.git data/awesome-selfhosted-data
   fi
   ```

   Completion criterion: `data/awesome-selfhosted-data/software/*.yml` exists and can be parsed.

2. **Parse software entries.** Read each YAML file under `software/`. Important fields:

   | Field | Use |
   |---|---|
   | `name` | Display name |
   | `website_url` | User-facing site |
   | `description` | Matching and summary |
   | `licenses` | Legal/commercial constraints |
   | `platforms` | Docker, PHP, Nodejs, Python, Go, K8S, deb, etc. |
   | `tags` | Category matching |
   | `source_code_url` | Trust and follow-up inspection |
   | `demo_url` | UX preview when available |
   | `stargazers_count` | Community signal, not absolute quality |
   | `updated_at`, `current_release`, `commit_history` | Maintenance signal |
   | `archived` | Exclude or warn |
   | `depends_3rdparty` | Warn about external-service dependencies |

   Completion criterion: parser reports item count and zero YAML failures.

3. **Map the user’s need to search terms.** Extract category words and SaaS analogies. Examples:

   | User language | Likely tags / keywords |
   |---|---|
   | Notion, knowledge base, second brain | `Knowledge Management Tools`, `Note-taking & Editors`, `Wikis` |
   | Zapier, Make, workflow automation | `Automation`, `Software Development - Low Code` |
   | Google Analytics, product analytics | `Analytics` |
   | Dropbox, file sharing, upload | `File Transfer & Synchronization`, `File Transfer - Single-click & Drag-n-drop Upload`, `File Transfer - Object Storage & File Servers` |
   | YouTube, video, streaming | `Media Streaming - Video Streaming`, `Media Management` |
   | Jira, Trello, project management | `Software Development - Project Management`, `Task Management & To-do Lists`, `Ticketing` |
   | ChatGPT UI, RAG, local LLM | `Generative Artificial Intelligence (GenAI)` |
   | status page, uptime | `Monitoring & Status Pages` |

   Completion criterion: at least one tag or keyword group is chosen before scoring.

4. **Filter first, then score.** Default filters:

   - Exclude `archived: true` unless the user asks for historical projects.
   - Exclude `⊘ Proprietary` unless the user allows closed-source or commercial software.
   - Prefer entries with `source_code_url`.
   - Prefer `Docker` for personal/VPS deployment unless the user asks for another stack.
   - Warn on `depends_3rdparty: true` if the user wants fully offline/private deployment.

   Completion criterion: explain any hard filters that materially changed the result set.

5. **Score candidates.** Use this lightweight model as a guide, not a black box:

   | Signal | Suggested weight |
   |---|---:|
   | Strong tag match | +30 |
   | Name/description keyword match | +20 |
   | Docker support | +15 |
   | Recently maintained / has release metadata | +15 |
   | Community signal from stars | +10 |
   | Demo URL exists | +5 |
   | Proprietary license | exclude or -50 |
   | Archived | exclude or -50 |
   | K8S-only or heavy multi-service deployment for small VPS | -5 to -20 |

   Completion criterion: shortlist is sorted by practical fit, not just stars.

6. **Return a decision-ready shortlist.** Include URLs and caveats. Minimum columns:

   | Column | Required content |
   |---|---|
   | Project | Name and website URL |
   | Why it fits | Concrete reason tied to user need |
   | Platform | Docker/PHP/Nodejs/Python/etc. |
   | License | Explicit license list |
   | Source | Repository/source URL |
   | Maintenance | Stars and updated/release signal when available |
   | Deployment difficulty | Low / Medium / High with one reason |
   | Cautions | AGPL/GPL, proprietary, heavy dependencies, external services, weak maintenance, unclear docs |

   Completion criterion: user can pick a project or reject the shortlist without asking “where is the link?”

## Output Format

Use concise Chinese by default if the user is Chinese. Use explicit URLs and paths.

Recommended structure:

```markdown
# 自托管软件推荐：<需求>

## 结论
我的首选是 <project>，因为 <reason>。

## 候选列表
| 排名 | 项目 | 适合原因 | 平台 | License | 源码 | 难度 | 风险 |
|---:|---|---|---|---|---|---|---|

## 推荐顺序
1. <project> — 最适合...
2. <project> — 适合...
3. <project> — 备选...

## 部署前必须确认
- 官方部署文档：<url>
- 资源需求：CPU/RAM/Disk
- 数据目录和备份策略
- 反向代理 / HTTPS / 域名
- 升级和回滚方式
```

## Deployment Follow-up Rules

When the user selects a project and asks to deploy:

1. Open the selected project’s official repository and documentation.
2. Verify the current install method; do not assume the awesome-selfhosted metadata is enough.
3. Prefer Docker Compose for VPS/personal-server deployments when officially supported.
4. Identify persistent volumes, environment variables, ports, database requirements, and upgrade instructions.
5. Generate nginx or Caddy reverse-proxy configuration only after confirming the project’s internal port and base URL behavior.
6. Include a backup plan before declaring deployment complete.
7. Run a health check after deployment and report the real URL/status.

Completion criterion: deployment advice is backed by the selected project’s current docs or real command output.

## Local Query CLI

The recommended entry point is the `nuwa-selfhosted` console script (installed via `pip install nuwa-selfhosted` or `pip install -e .` from a local checkout). It works on macOS and Windows.

```bash
nuwa-selfhosted query "notion knowledge base" --limit 5
nuwa-selfhosted query "zapier automation" --prefer-docker --limit 10
nuwa-selfhosted query --tag "Generative Artificial Intelligence (GenAI)" --limit 8 --json
nuwa-selfhosted query --tag ai --limit 5
nuwa-selfhosted update    # (re-)clone awesome-selfhosted-data
nuwa-selfhosted version   # prints 1.1.1
```

Subcommands:

- `query`   — search the catalog (accepts a free-text query and/or `--tag`).
- `update`  — clone or `git pull --ff-only` the local `awesome-selfhosted-data` checkout.
- `version` — print the package version.

Script fallback (still supported for backward compatibility):

```bash
python scripts/nuwa_selfhosted_query.py "notion knowledge base" --limit 8
```

The script is now a thin shim over `nuwa_selfhosted.cli:main`, so its arguments match the `query` subcommand exactly.

If neither the CLI nor the script is available, implement the same logic directly with Python: parse YAML, filter proprietary/archived entries, score by tags/keywords/platforms, and return a markdown table.

## Common Pitfalls

1. **Treating GitHub stars as quality.** Stars are only a community signal. A smaller but maintained Docker-first project may be the better recommendation.
2. **Ignoring AGPL/GPL obligations.** Always show licenses. Warn when server-side modifications and public service exposure may trigger obligations.
3. **Recommending proprietary entries by default.** `⊘ Proprietary` should be excluded unless the user accepts commercial/closed-source software.
4. **Assuming Docker means easy.** Some Docker apps still require external databases, object storage, workers, SSO, or heavy memory.
5. **Using stale metadata for deployment.** awesome-selfhosted is a directory. Official project docs are the deployment authority.
6. **Publishing private environment details.** Public repos and reusable examples must use placeholders only.
7. **Overloading the shortlist.** Return 3–8 strong candidates. If there are many, group by use case rather than dumping a giant table.

## Verification Checklist

- [ ] Data repository exists or was cloned successfully.
- [ ] YAML parse completed with item count and error count.
- [ ] User need was mapped to tags and keywords.
- [ ] Proprietary and archived entries were handled explicitly.
- [ ] Shortlist includes website/source URLs, license, platform, difficulty, and cautions.
- [ ] Recommendation is sorted by practical fit, not only stars.
- [ ] No private user information appears in generated files, public examples, commits, or repository descriptions.
- [ ] For deployment follow-up, official project docs were inspected before writing commands.
