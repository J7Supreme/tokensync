import copy
import json
import os


COLLECTIONS = ("semantic", "pattern", "component")
OUTPUT_FILES = (
    "adapters/figma/figma_tokens_adaptive.json",
    "adapters/figma/figma_tokens_4_collections.json",
)


def is_token_node(node):
    return isinstance(node, dict) and ("$value" in node or "value" in node)


def get_token_value(node):
    return node.get("$value", node.get("value"))


def infer_type_from_value(raw_value):
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


def infer_type_from_path(path):
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


def normalize_alias(raw_value, theme_name):
    if not (isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}")):
        return raw_value

    ref_path = raw_value[1:-1]
    if ref_path.startswith("primitive."):
        return raw_value

    if ref_path.startswith(("semantic.", "pattern.", "component.")):
        base_collection, remainder = ref_path.split(".", 1)
        return "{" + f"{base_collection}/{theme_name}.{remainder}" + "}"

    return raw_value


def normalize_nested_value(raw_value, theme_name):
    if isinstance(raw_value, dict):
        normalized = {}
        for key, value in raw_value.items():
            if isinstance(value, list):
                normalized[key] = [normalize_nested_value(item, theme_name) for item in value]
            else:
                normalized[key] = normalize_nested_value(value, theme_name)
        return normalized

    if isinstance(raw_value, list):
        return [normalize_nested_value(item, theme_name) for item in raw_value]

    return normalize_alias(raw_value, theme_name)


def normalize_tree(obj, prefix, theme_name):
    if not isinstance(obj, dict):
        return obj

    normalized = {}
    for key, value in obj.items():
        if key.startswith("$"):
            normalized[key] = copy.deepcopy(value)
            continue

        path = f"{prefix}.{key}" if prefix else key
        if is_token_node(value):
            token = copy.deepcopy(value)
            token["$value"] = normalize_nested_value(get_token_value(token), theme_name)
            token.pop("value", None)
            token.setdefault("$description", "")
            token.setdefault("$type", infer_type_from_path(path) or infer_type_from_value(token["$value"]))
            normalized[key] = token
        elif isinstance(value, dict):
            normalized[key] = normalize_tree(value, path, theme_name)
        else:
            normalized[key] = copy.deepcopy(value)

    return normalized


def flatten_tokens(obj, prefix=""):
    out = {}
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


def refine_alias_types(payload):
    flat = {}
    for top_key, top_value in payload.items():
        if top_key.startswith("$"):
            continue
        flat.update(flatten_tokens(top_value, top_key))

    cache = {}

    def infer(path):
        if path in cache:
            return cache[path]
        node = flat.get(path)
        if not node:
            return None
        explicit = node.get("$type")
        raw_value = node.get("$value")
        if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
            ref_path = raw_value[1:-1]
            ref_type = infer(ref_path)
            if ref_type:
                cache[path] = ref_type
                return ref_type
        cache[path] = explicit
        return explicit

    for path, node in flat.items():
        raw_value = node.get("$value")
        if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
            inferred = infer(path)
            if inferred and node.get("$type") != inferred:
                node["$type"] = inferred


def build_payload(source_data):
    payload = {
        "primitive": {
            "primitive": normalize_tree(
                source_data.get("Primitive", {}).get("primitive", {}),
                "primitive",
                "base",
            )
        }
    }

    for theme_name, source_theme in (("light", "Light"), ("dark", "Dark")):
        theme_root = source_data.get(source_theme, {})
        for collection in COLLECTIONS:
            payload[f"{collection}/{theme_name}"] = normalize_tree(
                theme_root.get(collection, {}),
                collection,
                theme_name,
            )

    payload["$themes"] = [
        {
            "id": "light",
            "name": "Light",
            "selectedTokenSets": {
                "primitive": "enabled",
                "semantic/light": "enabled",
                "semantic/dark": "disabled",
                "pattern/light": "enabled",
                "pattern/dark": "disabled",
                "component/light": "enabled",
                "component/dark": "disabled",
            },
        },
        {
            "id": "dark",
            "name": "Dark",
            "selectedTokenSets": {
                "primitive": "enabled",
                "semantic/light": "disabled",
                "semantic/dark": "enabled",
                "pattern/light": "disabled",
                "pattern/dark": "enabled",
                "component/light": "disabled",
                "component/dark": "enabled",
            },
        },
    ]

    payload["$metadata"] = {
        "tokenSetOrder": [
            "primitive",
            "semantic/light",
            "semantic/dark",
            "pattern/light",
            "pattern/dark",
            "component/light",
            "component/dark",
        ]
    }

    refine_alias_types(payload)
    return payload


def write_payload(payload):
    os.makedirs("adapters/figma", exist_ok=True)
    for out_path in OUTPUT_FILES:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")


def main():
    with open("source/tokens.json", "r", encoding="utf-8") as f:
        source_data = json.load(f)

    payload = build_payload(source_data)
    write_payload(payload)

    print("Generated:")
    for out_path in OUTPUT_FILES:
        print(f"- {out_path}")


if __name__ == "__main__":
    main()
