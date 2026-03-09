# Notion Record Router Skill

Codex skill for routing structured content into the correct Notion database.

It classifies or accepts an explicit content type, picks the matching template, maps fields into Notion properties, and creates a page through the Notion API.

## Repository Layout

- `notion-record-router/`
  The skill folder.
- `notion-record-router/SKILL.md`
  Skill instructions and usage flow.
- `notion-record-router/scripts/notion_route_upload.py`
  Local script that routes one JSON record and uploads it to Notion.
- `notion-record-router/references/notion-config.example.json`
  Example config for `issue`, `article`, and `idea` routes.

## Supported Content Types

- `issue`
  Bug fix and troubleshooting notes.
- `article`
  Article or news summaries.
- `idea`
  Idea cards and lightweight notes.

You can add more routes by extending the JSON config.

## Requirements

- Python 3
- A Notion integration token in `NOTION_API_KEY`
- Notion database or data source IDs
- Integration access granted to those targets

## Quick Start

1. Copy `notion-record-router/references/notion-config.example.json` to your own config file.
2. Replace the placeholder `data_source_id` values and property names with your Notion schema.
3. Export your Notion token:

```bash
export NOTION_API_KEY="your-token"
```

4. Run a dry run first:

```bash
python3 notion-record-router/scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --input notion-record-router/references/sample-issue-record.json \
  --dry-run
```

5. Upload for real:

```bash
python3 notion-record-router/scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --input notion-record-router/references/sample-issue-record.json
```

## Notes

- Prefer `data_source_id` when targeting modern Notion databases.
- Use `--dry-run` before the first real upload for each route.
- Keep one config per Notion workspace or schema variant if your databases differ.
