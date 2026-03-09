#!/usr/bin/env python3
"""Route a structured record to the correct Notion database and create a page."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z0-9_.-]+)\s*}}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to the routing config JSON file.")
    parser.add_argument("--input", help="Path to a JSON file containing one record.")
    parser.add_argument("--json", help="Inline JSON record.")
    parser.add_argument("--type", dest="forced_type", help="Force a route instead of auto-detecting.")
    parser.add_argument("--dry-run", action="store_true", help="Print the rendered request instead of uploading.")
    return parser.parse_args()


def load_json(path: str | None, inline_json: str | None) -> dict[str, Any]:
    if bool(path) == bool(inline_json):
        raise ValueError("Pass exactly one of --input or --json.")
    if path:
        return json.loads(Path(path).read_text())
    return json.loads(inline_json or "{}")


def render_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        items = [render_scalar(item) for item in value if render_scalar(item)]
        if not items:
            return ""
        return "\n".join(f"- {item}" for item in items)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def lookup_field(payload: dict[str, Any], field: str) -> Any:
    current: Any = payload
    for part in field.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def render_template(template: str, payload: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        return render_scalar(lookup_field(payload, match.group(1)))

    return PLACEHOLDER_RE.sub(replace, template).strip()


def select_route(config: dict[str, Any], payload: dict[str, Any], forced_type: str | None) -> tuple[str, dict[str, Any]]:
    routes = config.get("routes", {})
    if not routes:
        raise ValueError("Config must define at least one route.")

    if forced_type:
        if forced_type not in routes:
            raise ValueError(f"Unknown route '{forced_type}'. Available routes: {', '.join(sorted(routes))}")
        return forced_type, routes[forced_type]

    explicit_type = payload.get("type")
    if explicit_type:
        if explicit_type not in routes:
            raise ValueError(f"Payload type '{explicit_type}' is not defined in config.")
        return explicit_type, routes[explicit_type]

    haystack = json.dumps(payload, ensure_ascii=False).lower()
    for route_name, route in routes.items():
        match = route.get("match", {})
        fields = match.get("any_of_fields", [])
        if any(lookup_field(payload, field) not in (None, "", [], {}) for field in fields):
            return route_name, route
        keywords = [str(keyword).lower() for keyword in match.get("any_of_keywords", [])]
        if any(keyword in haystack for keyword in keywords):
            return route_name, route

    raise ValueError("Could not determine a route. Add payload.type or update config match rules.")


def build_property_value(spec: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    prop_type = spec["type"]
    if "template" in spec:
        raw_value = render_template(spec["template"], payload)
    else:
        raw_value = lookup_field(payload, spec.get("field", ""))

    if prop_type == "title":
        return {"title": [{"type": "text", "text": {"content": str(raw_value or "")}}]}
    if prop_type == "rich_text":
        return {"rich_text": [{"type": "text", "text": {"content": str(raw_value or "")}}]}
    if prop_type == "select":
        return {"select": {"name": str(raw_value or "")}} if raw_value else {"select": None}
    if prop_type == "multi_select":
        values = raw_value if isinstance(raw_value, list) else ([raw_value] if raw_value else [])
        return {"multi_select": [{"name": str(value)} for value in values if str(value).strip()]}
    if prop_type == "url":
        return {"url": str(raw_value or "") or None}
    if prop_type == "date":
        return {"date": {"start": str(raw_value)}} if raw_value else {"date": None}
    if prop_type == "checkbox":
        return {"checkbox": bool(raw_value)}
    raise ValueError(f"Unsupported property type: {prop_type}")


def build_request(config: dict[str, Any], route_name: str, route: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    parent = None
    if route.get("data_source_id"):
        parent = {"data_source_id": route["data_source_id"]}
    elif route.get("database_id"):
        parent = {"database_id": route["database_id"]}
    elif route.get("page_id"):
        parent = {"page_id": route["page_id"]}
    if not parent:
        raise ValueError(f"Route '{route_name}' is missing a parent target (data_source_id, database_id, or page_id).")

    markdown_template = route.get("markdown_template")
    if not markdown_template:
        raise ValueError(f"Route '{route_name}' is missing markdown_template.")

    properties: dict[str, Any] = {}
    for property_name, spec in route.get("properties", {}).items():
        properties[property_name] = build_property_value(spec, payload)

    return {
        "parent": parent,
        "properties": properties,
        "markdown": render_template(markdown_template, payload),
    }


def upload_to_notion(config: dict[str, Any], request_body: dict[str, Any]) -> dict[str, Any]:
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        raise RuntimeError("NOTION_API_KEY is not set.")

    notion_version = config.get("notion_version", "2025-09-03")
    request = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": notion_version,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API error {exc.code}: {detail}") from exc


def main() -> int:
    args = parse_args()
    config = json.loads(Path(args.config).read_text())
    payload = load_json(args.input, args.json)
    route_name, route = select_route(config, payload, args.forced_type)
    request_body = build_request(config, route_name, route, payload)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "selected_route": route_name,
                    "request_body": request_body,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    response = upload_to_notion(config, request_body)
    print(json.dumps({"selected_route": route_name, "notion_response": response}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
