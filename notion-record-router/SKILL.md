---
name: notion-record-router
description: Route structured note content into the correct Notion database using a local config file, content-type templates, and the Notion API. Use when Codex needs to classify content such as bug fixes, article summaries, or idea notes, choose the matching template, and create a page in the corresponding Notion database.
---

# Notion Record Router

Route a structured record into the right Notion database. Keep the skill generic: configure database IDs and property mappings in JSON, then let the script choose the matching content type and upload the page.

## Quick Decision

- First-time setup:
  Read [`references/config-schema.md`](references/config-schema.md), copy the example config, fill real Notion targets, and verify integration permissions before running the script.
- Daily upload:
  Prepare one record, prefer an explicit `type`, run `--dry-run`, then upload.
- Extend a new content type:
  Add a route in the config with one target, property mappings, match rules, and a markdown template. Test it with a sample record before real uploads.
- Debug a failed upload:
  Use the failure table below before editing the script.

## Preflight Checklist

Before any upload, confirm all of the following:

- `NOTION_API_KEY` is set
- the Notion integration has access to the target database or data source
- the route target is real, not a placeholder
- the Notion property names in config match the actual schema
- the record has a clear `type`, or the match rules are specific enough to avoid misrouting

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

## Raw Material to Record

Do not assume the input is already structured. In real usage, the source is often:

- a link plus a short note
- copied text from an article
- a bug summary plus logs
- one sentence of raw thought

Convert raw material into one structured record before upload.

Use these minimal shapes:

- `issue`: `title` plus one of `symptom`, `root_cause`, or `fix`
- `article`: `title` plus `summary` or `why_it_matters`
- `idea`: `title` plus `idea` or `why_record`

If the material cannot be reduced to one clear record, stop and ask for a narrower input.

## Core Workflow

1. Choose the route.
   Prefer `payload.type`. Use auto-detection only when field-level matches are reliable.
2. Prepare one record.
   Keep the record scoped to one note, one article, one issue, or one idea.
3. Run `--dry-run`.
   Inspect the selected route, target parent, mapped properties, and rendered markdown.
4. Upload for real.
   Only upload after the dry run looks correct.
5. If upload fails, use the failure table before changing code or config blindly.

## Commands

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

## Failure Handling

Use this table before editing the script.

| Failure | Likely cause | Action |
| --- | --- | --- |
| `NOTION_API_KEY is not set` | Missing token | Export the token and retry |
| Route cannot be determined | Input too vague or match rules too weak | Add `type` or tighten the route config |
| Parent target missing | Route has no `data_source_id`, `database_id`, or `page_id` | Fix the config |
| Notion permission error | Integration not shared to the target | Share the integration to the target and retry |
| Notion schema or validation error | Property names or property types do not match | Compare the config against the real Notion schema |
| Wrong route selected in dry run | Match rules too broad | Use explicit `type` and narrow the match rules |

If the dry run already looks wrong, do not upload.

## Extend a New Route

1. Copy an existing route in the config.
2. Set one real target: `data_source_id`, `database_id`, or `page_id`.
3. Add the property mappings for that content type.
4. Write the markdown template.
5. Add narrow `match` rules.
6. Create one sample record and run `--dry-run`.
7. Upload only after the dry run is correct.

## Safety

- Run with `--dry-run` before the first real upload for each route.
- Do not guess Notion IDs; copy the route target from Notion and keep it in the config file. Prefer `data_source_id` for modern database-backed workflows.
- Keep the integration scoped only to the databases it should write to.
- If Notion returns a schema or permissions error, inspect the config before retrying.

## Files

- `scripts/notion_route_upload.py`: classify, render, and upload a record.
- [`references/config-schema.md`](references/config-schema.md): config format and field meanings.
- `references/notion-config.example.json`: example routes for issue/article/idea records.
- `references/sample-*.json`: example records for dry runs.
