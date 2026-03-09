# Notion Record Router Skill

English | [中文](#中文说明)

Route structured content into the correct Notion database with a configurable Codex skill.

This repository contains a reusable Codex skill plus a local Python script that:

- classifies content or accepts an explicit content type
- selects the matching template
- maps fields to Notion properties
- creates a page in the target Notion data source

It is designed for personal knowledge systems and AI-assisted note pipelines such as:

- issue and bug-fix records
- article and news summaries
- idea cards and lightweight notes

## Features

- Config-driven routing by content type
- Template-based markdown page generation
- Property mapping for Notion database fields
- `--dry-run` mode for safe preview
- Easy extension for new record types

## Repository Structure

```text
.
├── README.md
└── notion-record-router/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── scripts/notion_route_upload.py
    └── references/
        ├── config-schema.md
        ├── notion-config.example.json
        └── sample-issue-record.json
```

## How It Works

1. Prepare one structured JSON record.
2. Choose a route by `type`, or let the script auto-detect a route from configured match rules.
3. Render the configured markdown template.
4. Map selected fields into Notion properties.
5. Create a page through the Notion API.

## Supported Default Routes

The example config includes these routes:

- `issue`
  Bug fixes, troubleshooting notes, crash analysis
- `article`
  Article summaries, news digests, policy notes
- `idea`
  Idea cards, raw thoughts, future directions

You can add more routes in the config without changing the script.

## Requirements

- Python 3
- A Notion integration token in `NOTION_API_KEY`
- Target Notion `data_source_id`, `database_id`, or `page_id`
- Integration access granted to the corresponding Notion targets

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/nedhuo/notion-record-router-skill.git
cd notion-record-router-skill
```

### 2. Prepare your config

Copy the example config and replace placeholder IDs and property names with your own Notion schema.

```bash
cp notion-record-router/references/notion-config.example.json /path/to/notion-config.json
```

### 3. Set your Notion token

```bash
export NOTION_API_KEY="your-token"
```

### 4. Run a dry run

```bash
python3 notion-record-router/scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --input notion-record-router/references/sample-issue-record.json \
  --dry-run
```

### 5. Upload for real

```bash
python3 notion-record-router/scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --input notion-record-router/references/sample-issue-record.json
```

## Input Options

Pass a record in one of two ways:

- `--input /path/to/record.json`
- `--json '{"type":"idea","title":"..."}'`

Optional override:

- `--type issue`

## Example Input

```json
{
  "type": "article",
  "title": "Android 16 changes to watch",
  "source": "Android Developers Blog",
  "source_url": "https://example.com/post",
  "date": "2026-03-09",
  "tags": ["android", "platform"],
  "summary": "Summarize the key changes.",
  "why_it_matters": "Affects compatibility planning.",
  "next_steps": ["Review migration impact", "Check app behavior"]
}
```

## Configuration

Read [notion-record-router/references/config-schema.md](notion-record-router/references/config-schema.md) for the full config shape.

Each route defines:

- a Notion target
- matching rules
- property mappings
- a markdown template

The script prefers `data_source_id` for newer Notion API usage, and also supports `database_id` or `page_id`.

## Safety Notes

- Run `--dry-run` before the first real upload for each route.
- Keep route matching conservative to avoid writing to the wrong database.
- Scope your Notion integration to only the databases it needs.
- Keep one config per Notion workspace or schema variant when needed.

## Limitations

- This repository does not yet include automatic schema discovery from Notion.
- The built-in example routes cover only `issue`, `article`, and `idea`.
- Full validation against your real Notion schema depends on your own IDs and property names.

## Development

The main entry point is:

- [notion-record-router/scripts/notion_route_upload.py](notion-record-router/scripts/notion_route_upload.py)

The skill instructions live in:

- [notion-record-router/SKILL.md](notion-record-router/SKILL.md)

## License

No license file has been added yet. If you want to publish this as a standard open source project, add a `LICENSE` file before broader distribution.

## 中文说明

这是一个可配置的 Codex skill，用来把结构化内容自动路由到正确的 Notion 库。

仓库里包含两部分：

- 一个 Codex skill
- 一个本地 Python 脚本，用于根据内容类型选择模板并写入 Notion

它适合用在这些场景：

- 问题修复记录
- 文章和新闻摘要
- 灵感卡片
- 个人知识库归档

## 核心能力

- 按内容类型路由
- 用模板生成 Markdown 页面内容
- 将字段映射到 Notion 数据库属性
- 支持 `--dry-run` 预览
- 可以继续扩展更多内容类型

## 工作方式

1. 准备一条 JSON 格式的结构化记录
2. 脚本根据 `type` 或匹配规则选择路由
3. 套用对应模板生成 Markdown 内容
4. 将字段写入 Notion 属性
5. 通过 Notion API 创建页面

## 默认支持的内容类型

示例配置中包含三类：

- `issue`
  问题修复、Bug 排查、崩溃分析
- `article`
  文章摘要、新闻整理、政策速记
- `idea`
  灵感卡片、零散想法、后续方向

你可以只改配置文件来增加新的类型，不需要改脚本。

## 使用要求

- Python 3
- 设置环境变量 `NOTION_API_KEY`
- 准备好 Notion 的 `data_source_id`、`database_id` 或 `page_id`
- 对应的 Notion integration 已授权访问目标库

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/nedhuo/notion-record-router-skill.git
cd notion-record-router-skill
```

### 2. 准备配置文件

复制示例配置文件，并把里面的占位 ID 和属性名改成你自己的 Notion 库结构。

```bash
cp notion-record-router/references/notion-config.example.json /path/to/notion-config.json
```

### 3. 设置 Notion Token

```bash
export NOTION_API_KEY="你的 token"
```

### 4. 先做一次 dry run

```bash
python3 notion-record-router/scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --input notion-record-router/references/sample-issue-record.json \
  --dry-run
```

### 5. 正式上传

```bash
python3 notion-record-router/scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --input notion-record-router/references/sample-issue-record.json
```

## 输入方式

支持两种输入：

- `--input /path/to/record.json`
- `--json '{"type":"idea","title":"..."}'`

也支持用 `--type` 强制指定路由。

## 配置说明

完整配置格式见：

- [notion-record-router/references/config-schema.md](notion-record-router/references/config-schema.md)

每个路由需要定义：

- Notion 写入目标
- 匹配规则
- 属性映射
- Markdown 模板

脚本优先使用 `data_source_id`，同时兼容 `database_id` 和 `page_id`。

## 注意事项

- 每个新路由第一次使用都先跑 `--dry-run`
- 匹配规则尽量保守，避免写错库
- Notion integration 只给必要权限
- 如果不同库结构不一样，最好拆成不同配置文件

## 当前限制

- 还没有做 Notion schema 自动读取
- 内置示例只覆盖 `issue`、`article`、`idea`
- 是否能完全写入成功，取决于你的真实库字段配置是否一致

## 开发入口

主要脚本：

- [notion-record-router/scripts/notion_route_upload.py](notion-record-router/scripts/notion_route_upload.py)

Skill 说明：

- [notion-record-router/SKILL.md](notion-record-router/SKILL.md)

## 开源说明

目前仓库还没有单独加入 `LICENSE` 文件。如果你准备把它作为正式开源项目长期公开，建议补一个明确的许可证。
