# Nuwa Selfhosted

Nuwa Selfhosted is a Hermes Agent skill **and** a small Python package for finding, comparing, and planning deployments of self-hosted software using the public [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) ecosystem.

It is designed for practical software selection:

- Find open-source or self-hosted alternatives to SaaS tools.
- Prefer Docker-friendly options for VPS or personal servers.
- Filter out proprietary or archived entries by default.
- Show licenses, source URLs, deployment difficulty, and cautions.
- Keep the catalog fresh by reading `awesome-selfhosted-data` dynamically instead of embedding a stale list.

**Author:** ReyMao — **License:** MIT — **Version:** 1.1.1

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

## Repository layout

```text
SKILL.md                              Hermes skill instructions
pyproject.toml                        Package metadata (PEP 621)
src/nuwa_selfhosted/                  Python package
  ├── __init__.py                     __version__ = "1.1.1"
  ├── cli.py                          `nuwa-selfhosted` entry point (argparse)
  └── query.py                        Core query / scoring logic
scripts/nuwa_selfhosted_query.py      Backward-compatible shim -> nuwa_selfhosted.cli:main
README.md                             This file
LICENSE                               MIT license (© 2026 ReyMao)
.gitignore                            Keeps caches and private files out of git
```

## 安装 (macOS / Windows)

> `nuwa-selfhosted` 是纯 Python 包，`pip install` 后即得到 `nuwa-selfhosted` 命令行工具。

### 依赖

- Python **3.9+**
- `git` on `$PATH`（首次运行会自动 `git clone` awesome-selfhosted-data）
- 运行时依赖 `PyYAML`（由 `pyproject.toml` 声明，`pip install` 时自动安装）

### macOS

```bash
# 从 PyPI 安装（发布后）
python3 -m pip install --user nuwa-selfhosted

# 或者从本地源码安装（开发模式）
git clone https://github.com/reymondmeking-dot/nuwa-selfhosted.git
cd nuwa-selfhosted
python3 -m pip install -e .

# 校验安装
nuwa-selfhosted version   # -> 1.1.1
```

### Windows

`pip` 通常在 `PATH` 上；如果没有，可以用 `py -m pip` 代替。

```powershell
:: PowerShell / cmd
py -m pip install --user nuwa-selfhosted

:: 或者从本地源码安装
git clone https://github.com/reymondmeking-dot/nuwa-selfhosted.git
cd nuwa-selfhosted
py -m pip install -e .

:: 校验
nuwa-selfhosted version
```

如果 `nuwa-selfhosted` 命令找不到，说明 pip 的 `Scripts` 目录不在 `PATH`；可以直接调用：

```powershell
py -m nuwa_selfhosted.cli version
```

## 使用示例

```bash
# 关键词查询（默认 Markdown 表格）
nuwa-selfhosted query "notion knowledge base" --limit 5

# 按 tag 查询
nuwa-selfhosted query --tag ai --limit 5
nuwa-selfhosted query --tag "Generative Artificial Intelligence (GenAI)" --limit 8

# 只保留 Docker 项目 + JSON 输出（便于脚本消费）
nuwa-selfhosted query "file storage" --docker-only --limit 10 --json

# 允许出现商业闭源 / 已归档条目
nuwa-selfhosted query "self hosting panel" --include-proprietary
nuwa-selfhosted query "wiki" --include-archived

# 自定义数据缓存目录
nuwa-selfhosted query "analytics" --data /path/to/awesome-selfhosted-data --limit 10

# 手动更新数据仓库
nuwa-selfhosted update
```

环境变量 `NUWA_SELFHOSTED_DATA` 可以覆盖默认的数据目录（默认为 `data/awesome-selfhosted-data`）。

## Privacy

This repository intentionally contains no private server information, credentials, domains, phone numbers, IP addresses, SSH paths, or API keys.

Public examples use placeholders only:

```text
example.com
YOUR_SERVER_IP
/path/to/app
<token>
```

## Install as a Hermes skill

Install directly from GitHub:

```bash
hermes skills install https://raw.githubusercontent.com/reymondmeking-dot/nuwa-selfhosted/main/SKILL.md
```

From a local checkout:

```bash
hermes skills install ./SKILL.md
```

Or copy this folder into your Hermes skills directory as `nuwa-selfhosted`.

## Legacy script (backward compatible)

The old `scripts/nuwa_selfhosted_query.py` still works as a thin shim over the new CLI:

```bash
python scripts/nuwa_selfhosted_query.py "notion knowledge base" --limit 8
python scripts/nuwa_selfhosted_query.py "ai chat rag" --tag "Generative Artificial Intelligence (GenAI)" --json
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

## Author & License

- Author: **ReyMao**
- License: MIT — see [`LICENSE`](./LICENSE)
