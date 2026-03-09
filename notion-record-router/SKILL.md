---
name: notion-record-router
description: Route structured note content into the correct Notion database using a local config file, content-type templates, and the Notion API. Use when Codex needs to classify content such as bug fixes, article summaries, or idea notes, choose the matching template, and create a page in the corresponding Notion database.
---

# Notion Record Router

Route a structured record into the right Notion database. Keep the skill generic: configure database IDs and property mappings in JSON, then let the script choose the matching content type and upload the page.

## Workflow

1. Read [`references/config-schema.md`](references/config-schema.md) if the config file needs to be created or changed.
2. Confirm `NOTION_API_KEY` is set and the integration has access to the target databases.
3. Prepare a JSON payload for one record. Prefer an explicit `type`; fall back to auto-detection only when the record clearly matches one of the configured patterns.
4. Run `scripts/notion_route_upload.py` with `--dry-run` first to inspect the rendered Notion request.
5. Run the same command without `--dry-run` to create the page in Notion.

## Input Shape

Pass a JSON object with fields that the chosen template expects. The script supports any fields referenced by the config, but the default patterns are designed for:

- `issue`: bug fix / troubleshooting notes
- `article`: article or news summaries
- `idea`: idea cards and raw thoughts

Prefer these top-level fields when available:

- `type`
- `title`
- `tags`
- `date`
- `source`
- `source_url`

Store richer fields inside the same object, for example `symptom`, `root_cause`, `summary`, `why_it_matters`, `idea`, or `next_steps`.

## Command

```bash
python3 scripts/notion_route_upload.py \
  --config references/notion-config.example.json \
  --input /path/to/record.json \
  --dry-run
```

Upload for real:

```bash
python3 scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --input /path/to/record.json
```

Or pass inline JSON:

```bash
python3 scripts/notion_route_upload.py \
  --config /path/to/notion-config.json \
  --json '{"type":"idea","title":"内容选题","idea":"做一组社火帽子场景图文"}' \
  --dry-run
```

## Routing Rules

- If `type` exists and matches a configured route, use it.
- Otherwise, use the route's `match.any_of_fields` or `match.any_of_keywords`.
- If nothing matches, stop and ask for a clearer type or update the config.

Keep the auto-detection rules conservative. Wrong-database writes are more expensive than asking for one extra field.

## Template Rules

- Put database IDs, property mappings, and markdown templates in the JSON config.
- Keep the page body in markdown so AI-generated content stays easy to inspect and reuse.
- Use `{{field_name}}` placeholders. Missing fields render as empty strings.
- For list fields, the script renders bullet lists in markdown and arrays for `multi_select`.

## Property Mapping

Each route can map payload fields into Notion database properties. Supported property types are:

- `title`
- `rich_text`
- `select`
- `multi_select`
- `url`
- `date`
- `checkbox`

Use `field` for direct mapping or `template` for rendered values. Keep property names identical to the Notion database schema.

## Safety

- Run with `--dry-run` before the first real upload for each route.
- Do not guess Notion IDs; copy the route target from Notion and keep it in the config file. Prefer `data_source_id` for modern database-backed workflows.
- Keep the integration scoped only to the databases it should write to.
- If Notion returns a schema or permissions error, inspect the config before retrying.

## Files

- `scripts/notion_route_upload.py`: classify, render, and upload a record.
- [`references/config-schema.md`](references/config-schema.md): config format and field meanings.
- `references/notion-config.example.json`: example routes for issue/article/idea records.
