import argparse
import copy
import json
import os
from typing import Any, Dict, List, Optional, Set


THEMES = ("light", "dark")
SOURCE_THEME_KEYS = {"light": "Light", "dark": "Dark"}
COLLECTIONS = ("semantic", "pattern", "component")


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


def build_lookups(source_data: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    lookups: Dict[str, Dict[str, Dict[str, Any]]] = {
        "primitive": flatten_tokens(source_data.get("Primitive", {}).get("primitive", {}), "primitive")
    }
    for theme_name, source_theme in SOURCE_THEME_KEYS.items():
        theme_root = source_data.get(source_theme, {})
        themed_tokens: Dict[str, Dict[str, Any]] = {}
        for collection in COLLECTIONS:
            themed_tokens.update(flatten_tokens(theme_root.get(collection, {}), collection))
        lookups[theme_name] = themed_tokens
    return lookups


def collect_alias_refs(raw_value: Any) -> List[str]:
    refs: List[str] = []
    if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
        refs.append(raw_value[1:-1])
    elif isinstance(raw_value, dict):
        for value in raw_value.values():
            refs.extend(collect_alias_refs(value))
    elif isinstance(raw_value, list):
        for item in raw_value:
            refs.extend(collect_alias_refs(item))
    return refs


def validate_source(source_data: Dict[str, Any], lookups: Dict[str, Dict[str, Dict[str, Any]]]) -> None:
    for collection in COLLECTIONS:
        light_paths = set(flatten_tokens(source_data.get("Light", {}).get(collection, {}), collection).keys())
        dark_paths = set(flatten_tokens(source_data.get("Dark", {}).get(collection, {}), collection).keys())
        if light_paths != dark_paths:
            missing_in_dark = sorted(light_paths - dark_paths)
            missing_in_light = sorted(dark_paths - light_paths)
            raise ValueError(
                f"{collection} theme mismatch. Missing in Dark: {missing_in_dark[:5]} Missing in Light: {missing_in_light[:5]}"
            )

    for theme_name in THEMES:
        for path, node in lookups[theme_name].items():
            explicit_type = node.get("$type") or infer_type_from_path(path) or infer_type_from_value(get_token_value(node))
            if path.startswith("component.") and len(path.split(".")) < 5:
                raise ValueError(f"Invalid component path: {path}")
            if path.startswith("pattern.") and len(path.split(".")) < 4:
                raise ValueError(f"Invalid pattern path: {path}")
            if path.startswith(("pattern.", "component.")):
                refs = collect_alias_refs(get_token_value(node))
                for ref in refs:
                    if not ref.startswith(("semantic.", "primitive.")):
                        raise ValueError(f"Invalid reference {ref} in {path}")
            sibling_node = lookups["dark" if theme_name == "light" else "light"].get(path)
            if sibling_node:
                sibling_type = sibling_node.get("$type") or infer_type_from_path(path) or infer_type_from_value(get_token_value(sibling_node))
                if explicit_type != sibling_type:
                    raise ValueError(f"Type mismatch across themes for {path}: {explicit_type} vs {sibling_type}")


def resolve_value(
    raw_value: Any,
    theme_name: str,
    lookups: Dict[str, Dict[str, Dict[str, Any]]],
    cache: Dict[str, Any],
    stack: Set[str],
) -> Any:
    if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
        ref_path = raw_value[1:-1]
        if ref_path in stack:
            raise ValueError(f"Circular token alias detected: {' -> '.join(list(stack) + [ref_path])}")
        node = lookups["primitive"].get(ref_path) if ref_path.startswith("primitive.") else lookups[theme_name].get(ref_path)
        if not node:
            raise ValueError(f"Unresolved reference {ref_path}")
        return resolve_token(ref_path, node, theme_name, lookups, cache, stack)
    if isinstance(raw_value, dict):
        resolved: Dict[str, Any] = {}
        for key, value in raw_value.items():
            if key == "stops" and isinstance(value, list):
                resolved[key] = [resolve_value(stop, theme_name, lookups, cache, stack) for stop in value]
            else:
                resolved[key] = resolve_value(value, theme_name, lookups, cache, stack)
        return resolved
    if isinstance(raw_value, list):
        return [resolve_value(item, theme_name, lookups, cache, stack) for item in raw_value]
    return raw_value


def resolve_token(
    path: str,
    node: Dict[str, Any],
    theme_name: str,
    lookups: Dict[str, Dict[str, Dict[str, Any]]],
    cache: Dict[str, Any],
    stack: Optional[Set[str]] = None,
) -> Any:
    cache_key = f"{theme_name}:{path}"
    if cache_key in cache:
        return cache[cache_key]
    stack = stack or set()
    stack.add(path)
    raw_value = copy.deepcopy(get_token_value(node))
    resolved = resolve_value(raw_value, theme_name, lookups, cache, stack)
    cache[cache_key] = resolved
    stack.remove(path)
    return resolved


def resolve_type(
    path: str,
    node: Dict[str, Any],
    theme_name: str,
    lookups: Dict[str, Dict[str, Dict[str, Any]]],
    cache: Dict[str, str],
) -> str:
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


def set_nested_leaf(target: Dict[str, Any], path_parts: List[str], leaf: Dict[str, Any]) -> None:
    current = target
    for part in path_parts[:-1]:
        current = current.setdefault(part, {})
    current[path_parts[-1]] = leaf


def build_runtime_canonical(source_data: Dict[str, Any]) -> Dict[str, Any]:
    lookups = build_lookups(source_data)
    validate_source(source_data, lookups)
    value_cache: Dict[str, Any] = {}
    type_cache: Dict[str, str] = {}

    payload: Dict[str, Any] = {
        "$themes": list(THEMES),
        "$metadata": {
            "collections": list(COLLECTIONS),
        },
    }

    for collection in COLLECTIONS:
        payload[collection] = {}
        light_flat = flatten_tokens(source_data.get("Light", {}).get(collection, {}), collection)
        for path, light_node in light_flat.items():
            leaf = {
                "$type": resolve_type(path, light_node, "light", lookups, type_cache),
                "$description": light_node.get("$description", ""),
                "sourceRef": path,
                "light": {
                    "value": resolve_token(path, light_node, "light", lookups, value_cache),
                    "sourceRef": path,
                },
            }
            dark_node = lookups["dark"][path]
            leaf["dark"] = {
                "value": resolve_token(path, dark_node, "dark", lookups, value_cache),
                "sourceRef": path,
            }
            set_nested_leaf(payload[collection], path.split(".")[1:], leaf)

    return payload


def flatten_runtime_modes(runtime_payload: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    flat_by_theme: Dict[str, Dict[str, Dict[str, Any]]] = {theme: {} for theme in THEMES}

    def walk(obj: Dict[str, Any], prefix: str) -> None:
        for key, value in obj.items():
            if key.startswith("$"):
                continue
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict) and "sourceRef" in value and "light" in value and "dark" in value:
                for theme in THEMES:
                    flat_by_theme[theme][path] = {
                        "type": value["$type"],
                        "description": value.get("$description", ""),
                        "sourceRef": value["sourceRef"],
                        "value": value[theme]["value"],
                    }
            elif isinstance(value, dict):
                walk(value, path)

    for collection in COLLECTIONS:
        walk(runtime_payload[collection], collection)
    return flat_by_theme


def make_css_value(token_type: str, value: Any) -> str:
    if token_type == "gradient" and isinstance(value, dict):
        angle = value.get("angle", 180)
        stops = value.get("stops", [])
        stop_str = ", ".join(f"{stop['color']} {int(stop['position'] * 100)}%" for stop in stops)
        return f"linear-gradient({angle}deg, {stop_str})"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def kebab(path: str) -> str:
    return path.replace(".", "-").replace("_", "-")


def build_css_payload(flat_by_theme: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"light": {"variables": {}}, "dark": {"variables": {}}}
    for theme in THEMES:
        for path, token in flat_by_theme[theme].items():
            payload[theme]["variables"][f"--{kebab(path)}"] = {
                "value": make_css_value(token["type"], token["value"]),
                "sourceRef": token["sourceRef"],
                "type": token["type"],
            }
    return payload


def build_tailwind_payload(flat_by_theme: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    category_map = {
        "color": "colors",
        "gradient": "backgroundImage",
        "dimension": "spacing",
        "spacing": "spacing",
        "sizing": "spacing",
        "borderRadius": "borderRadius",
        "number": "numbers",
        "string": "strings",
        "boolean": "booleans",
    }
    for theme in THEMES:
        theme_payload: Dict[str, Any] = {"theme": {"extend": {}}}
        for path, token in flat_by_theme[theme].items():
            category = category_map.get(token["type"], "tokens")
            theme_payload["theme"]["extend"].setdefault(category, {})
            theme_payload["theme"]["extend"][category][kebab(path)] = {
                "value": make_css_value(token["type"], token["value"]),
                "sourceRef": token["sourceRef"],
            }
        payload[theme] = theme_payload
    return payload


def build_react_payload(runtime_payload: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for theme in THEMES:
        theme_tree: Dict[str, Any] = {}

        def walk(obj: Dict[str, Any], target: Dict[str, Any]) -> None:
            for key, value in obj.items():
                if key.startswith("$"):
                    continue
                if isinstance(value, dict) and "sourceRef" in value and "light" in value and "dark" in value:
                    target[key] = {
                        "value": value[theme]["value"],
                        "sourceRef": value["sourceRef"],
                        "type": value["$type"],
                        "description": value.get("$description", ""),
                    }
                elif isinstance(value, dict):
                    target[key] = {}
                    walk(value, target[key])

        for collection in COLLECTIONS:
            theme_tree[collection] = {}
            walk(runtime_payload[collection], theme_tree[collection])
        payload[theme] = theme_tree
    return payload


def build_mobile_payload(flat_by_theme: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"ios": {}, "android": {}}
    for platform in payload:
        for theme in THEMES:
            payload[platform][theme] = {}
            for path, token in flat_by_theme[theme].items():
                payload[platform][theme][path] = {
                    "value": token["value"],
                    "sourceRef": token["sourceRef"],
                    "type": token["type"],
                }
    return payload


def write_json(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build runtime-facing adapters from a canonical token source.")
    parser.add_argument("--source", default="source/tokens.json", help="Path to the canonical token source JSON.")
    parser.add_argument("--output-dir", default="adapters/runtime", help="Directory for generated runtime adapter files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with open(args.source, "r", encoding="utf-8") as handle:
        source_data = json.load(handle)

    runtime_payload = build_runtime_canonical(source_data)
    flat_by_theme = flatten_runtime_modes(runtime_payload)

    outputs = {
        os.path.join(args.output_dir, "tokens.runtime.json"): runtime_payload,
        os.path.join(args.output_dir, "tokens.css.json"): build_css_payload(flat_by_theme),
        os.path.join(args.output_dir, "tokens.tailwind.json"): build_tailwind_payload(flat_by_theme),
        os.path.join(args.output_dir, "tokens.react.json"): build_react_payload(runtime_payload),
        os.path.join(args.output_dir, "tokens.mobile.json"): build_mobile_payload(flat_by_theme),
    }

    for path, payload in outputs.items():
        write_json(path, payload)

    print("Generated:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
