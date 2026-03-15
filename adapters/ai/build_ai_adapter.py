import copy
import json
import os
from typing import Any, Dict, List, Optional, Set


THEMES = ("light", "dark")
SOURCE_THEME_KEYS = {"light": "Light", "dark": "Dark"}
COLLECTIONS = ("primitive", "semantic", "pattern", "component")
OUTPUT_FILE = "adapters/ai/ai.tokens.json"


def is_token_node(node: Any) -> bool:
    return isinstance(node, dict) and ("$value" in node or "value" in node)


def get_token_value(node: Dict[str, Any]) -> Any:
    return node.get("$value", node.get("value"))


def flatten_tokens(obj: Dict[str, Any], prefix: str = "") -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if not isinstance(obj, dict):
        return out
    for key, value in obj.items():
        if key.startswith("$"):
            continue
        path = f"{prefix}.{key}" if prefix else key
        if is_token_node(value):
            out[path] = value
        elif isinstance(value, dict):
            out.update(flatten_tokens(value, path))
    return out


def infer_type_from_value(raw_value: Any) -> str:
    if isinstance(raw_value, bool):
        return "boolean"
    if isinstance(raw_value, (int, float)):
        return "number"
    if isinstance(raw_value, dict):
        if {"type", "angle", "stops"}.issubset(raw_value.keys()):
            return "gradient"
        return "string"
    if isinstance(raw_value, str):
        if raw_value == "[MISSING]":
            return "string"
        if raw_value.startswith("#") or raw_value.lower().startswith("rgb"):
            return "color"
        if raw_value.endswith("px"):
            return "dimension"
        lowered = raw_value.lower()
        if lowered in {"true", "false"}:
            return "boolean"
        try:
            float(raw_value)
            return "number"
        except ValueError:
            return "string"
    return "string"


def infer_type_from_path(path: str) -> Optional[str]:
    if any(
        segment in path
        for segment in (
            ".iconSize",
            ".padding",
            ".gap",
            ".height",
            ".width",
            ".paddingX",
            ".paddingY",
            ".paddingTop",
            ".dragHandleWidth",
            ".dragHandleHeight",
            ".closeButtonSize",
            ".contentTopGap",
            ".fieldPaddingX",
            ".fieldHeight",
            ".sectionGap",
            ".actionGap",
            ".rowGap",
        )
    ):
        return "dimension"
    if any(
        segment in path
        for segment in (".background", ".text", ".stroke", ".border", ".fill", ".backdrop", ".logo", ".icon")
    ):
        return "color"
    if ".spacing." in path:
        return "spacing"
    if ".size." in path:
        return "sizing"
    if ".radius." in path:
        return "borderRadius"
    return None


def collect_refs(raw_value: Any) -> List[str]:
    refs: List[str] = []
    if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
        refs.append(raw_value[1:-1])
    elif isinstance(raw_value, dict):
        for value in raw_value.values():
            refs.extend(collect_refs(value))
    elif isinstance(raw_value, list):
        for item in raw_value:
            refs.extend(collect_refs(item))
    return refs


def build_lookups(source_data: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    lookups: Dict[str, Dict[str, Dict[str, Any]]] = {
        "primitive": flatten_tokens(source_data.get("Primitive", {}).get("primitive", {}), "primitive")
    }
    for theme_name, source_theme in SOURCE_THEME_KEYS.items():
        theme_root = source_data.get(source_theme, {})
        theme_tokens: Dict[str, Dict[str, Any]] = {}
        for collection in ("semantic", "pattern", "component"):
            theme_tokens.update(flatten_tokens(theme_root.get(collection, {}), collection))
        lookups[theme_name] = theme_tokens
    return lookups


def resolve_value(raw_value: Any, theme_name: str, lookups: Dict[str, Dict[str, Dict[str, Any]]], cache: Dict[str, Any], stack: Set[str]) -> Any:
    if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
        ref_path = raw_value[1:-1]
        if ref_path in stack:
            raise ValueError(f"Circular token alias detected: {' -> '.join(list(stack) + [ref_path])}")
        target = lookups["primitive"].get(ref_path) if ref_path.startswith("primitive.") else lookups[theme_name].get(ref_path)
        if not target:
            raise ValueError(f"Unresolved reference {ref_path}")
        return resolve_token(ref_path, target, theme_name, lookups, cache, stack)
    if isinstance(raw_value, dict):
        return {key: resolve_value(value, theme_name, lookups, cache, stack) for key, value in raw_value.items()}
    if isinstance(raw_value, list):
        return [resolve_value(item, theme_name, lookups, cache, stack) for item in raw_value]
    return raw_value


def resolve_token(path: str, node: Dict[str, Any], theme_name: str, lookups: Dict[str, Dict[str, Dict[str, Any]]], cache: Dict[str, Any], stack: Optional[Set[str]] = None) -> Any:
    cache_key = f"{theme_name}:{path}"
    if cache_key in cache:
        return cache[cache_key]
    stack = stack or set()
    stack.add(path)
    resolved = resolve_value(copy.deepcopy(get_token_value(node)), theme_name, lookups, cache, stack)
    cache[cache_key] = resolved
    stack.remove(path)
    return resolved


def resolve_type(path: str, node: Dict[str, Any], theme_name: str, lookups: Dict[str, Dict[str, Dict[str, Any]]], cache: Dict[str, str]) -> str:
    cache_key = f"{theme_name}:{path}"
    if cache_key in cache:
        return cache[cache_key]
    explicit = node.get("$type")
    if explicit:
        cache[cache_key] = explicit
        return explicit
    raw_value = get_token_value(node)
    if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
        ref_path = raw_value[1:-1]
        target = lookups["primitive"].get(ref_path) if ref_path.startswith("primitive.") else lookups[theme_name].get(ref_path)
        if target:
            inferred = resolve_type(ref_path, target, theme_name, lookups, cache)
            cache[cache_key] = inferred
            return inferred
    inferred = infer_type_from_path(path) or infer_type_from_value(raw_value)
    cache[cache_key] = inferred
    return inferred


def build_layer_tree(paths: Dict[str, Dict[str, Any]], layer_name: str) -> Dict[str, Any]:
    tree: Dict[str, Any] = {}
    prefix = f"{layer_name}."
    for path, entry in paths.items():
        if not path.startswith(prefix):
            continue
        current = tree
        parts = path.split(".")[1:]
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = entry
    return tree


def build_component_index(entries: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    component_index: Dict[str, Any] = {}
    for path, entry in entries.items():
        if not path.startswith("component."):
            continue
        parts = path.split(".")
        if len(parts) < 5:
            continue
        _, component_name, variant, state, *rest = parts
        prop_name = ".".join(rest)
        comp = component_index.setdefault(component_name, {"variants": {}})
        variant_bucket = comp["variants"].setdefault(variant, {"states": {}})
        state_bucket = variant_bucket["states"].setdefault(state, {"properties": {}})
        state_bucket["properties"][prop_name] = {
            "path": path,
            "type": entry["type"],
            "description": entry.get("description", ""),
            "light": entry.get("light", {}),
            "dark": entry.get("dark", {}),
        }
    return component_index


def build_ai_payload(source_data: Dict[str, Any]) -> Dict[str, Any]:
    lookups = build_lookups(source_data)
    type_cache: Dict[str, str] = {}
    value_cache: Dict[str, Any] = {}
    flat_entries: Dict[str, Dict[str, Any]] = {}

    for path, node in lookups["primitive"].items():
        flat_entries[path] = {
            "layer": "primitive",
            "type": resolve_type(path, node, "light", lookups, type_cache),
            "description": node.get("$description", ""),
            "value": get_token_value(node),
            "resolved": get_token_value(node),
            "references": [],
            "sourceRef": path,
        }

    for theme_name in THEMES:
        for path, node in lookups[theme_name].items():
            entry = flat_entries.setdefault(
                path,
                {
                    "layer": path.split(".")[0],
                    "type": resolve_type(path, node, theme_name, lookups, type_cache),
                    "description": node.get("$description", ""),
                    "sourceRef": path,
                },
            )
            entry.setdefault(theme_name, {})
            entry[theme_name] = {
                "value": get_token_value(node),
                "resolved": resolve_token(path, node, theme_name, lookups, value_cache),
                "references": collect_refs(get_token_value(node)),
            }

    payload = {
        "$metadata": {
            "generatedFrom": "source/tokens.json",
            "adapter": "ai",
            "themes": list(THEMES),
            "layers": list(COLLECTIONS),
        },
        "tokens": {
            "primitive": build_layer_tree(flat_entries, "primitive"),
            "semantic": build_layer_tree(flat_entries, "semantic"),
            "pattern": build_layer_tree(flat_entries, "pattern"),
            "component": build_layer_tree(flat_entries, "component"),
        },
        "index": dict(sorted(flat_entries.items())),
        "componentIndex": build_component_index(flat_entries),
    }
    return payload


def write_payload(payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> None:
    with open("source/tokens.json", "r", encoding="utf-8") as f:
        source_data = json.load(f)

    payload = build_ai_payload(source_data)
    write_payload(payload)
    print(f"Generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
