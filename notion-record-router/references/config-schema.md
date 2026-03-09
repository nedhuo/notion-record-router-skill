# Config Schema

Use one JSON file to define routing, database targets, property mappings, and page markdown templates.

## File Shape

```json
{
  "notion_version": "2025-09-03",
  "routes": {
    "issue": {
      "data_source_id": "your-data-source-id",
      "match": {
        "any_of_fields": ["symptom", "root_cause", "fix"],
        "any_of_keywords": ["bug", "crash", "anr"]
      },
      "properties": {
        "Name": { "type": "title", "field": "title" },
        "Tags": { "type": "multi_select", "field": "tags" },
        "Date": { "type": "date", "field": "date" },
        "Source URL": { "type": "url", "field": "source_url" }
      },
      "markdown_template": "# {{title}}\n\n## 现象\n{{symptom}}"
    }
  }
}
```

## Top-Level Keys

- `notion_version`
  Use the Notion API version header. Default in the script is `2025-09-03`.
- `routes`
  Object keyed by route name. The route name is the `type` value you pass in the record.

## Route Keys

- `database_id`
  Legacy option. Target Notion database ID.
- `data_source_id`
  Preferred for Notion API version `2025-09-03`. Target data source ID.
- `page_id`
  Optional alternative when creating standalone child pages instead of database rows.
- `match`
  Optional. Used only when `type` is missing.
- `properties`
  Optional. Maps record fields into database properties.
- `markdown_template`
  Required. Full page body in markdown.

## Match Rules

`match.any_of_fields`

- Match when any listed field exists and is non-empty in the input record.

`match.any_of_keywords`

- Match when any keyword appears in the serialized record text.

Prefer field-based matching. Keywords are a fallback.

## Property Mapping

Supported property types:

- `title`
- `rich_text`
- `select`
- `multi_select`
- `url`
- `date`
- `checkbox`

Each property mapping supports:

- `type`
  Required.
- `field`
  Directly read this payload field.
- `template`
  Render this `{{placeholder}}` template from payload fields.

Use either `field` or `template`.

## Parent Selection

The script chooses the target in this order:

1. `data_source_id`
2. `database_id`
3. `page_id`

Use only one target field per route.

## Template Notes

- `{{field_name}}` inserts a scalar value.
- If the value is a list and used in markdown, it renders as a bullet list.
- Missing values become empty strings.

## Record Example

```json
{
  "type": "article",
  "title": "Android 16 新特性",
  "source": "Android Developers Blog",
  "source_url": "https://example.com/post",
  "date": "2026-03-09",
  "tags": ["android", "platform"],
  "summary": "总结核心变化。",
  "why_it_matters": "影响主业开发规划。",
  "next_steps": ["检查兼容性", "评估适配成本"]
}
```
