import copy
import json
import os


TOKEN_SETS = ("Primitive", "Light", "Dark")
THEME_SETS = ("Light", "Dark")


def is_token_node(node):
    return isinstance(node, dict) and ("$value" in node or "value" in node)


def get_token_value(node):
    return node.get("$value", node.get("value"))


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


def is_alias(raw_value):
    return isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}")


def infer_type_from_path(path):
    if path.startswith("primitive.spacing."):
        return "spacing"
    if path.startswith("primitive.size."):
        return "sizing"
    if path.startswith("primitive.radius."):
        return "string"
    return None


def build_lookup_tables(data):
    lookups = {"Primitive": {}, "Light": {}, "Dark": {}}

    primitive_root = data.get("Primitive", {})
    lookups["Primitive"].update(flatten_tokens(primitive_root, ""))

    for theme in THEME_SETS:
        theme_root = data.get(theme, {})
        lookups[theme].update(flatten_tokens(theme_root, ""))

    return lookups


def resolve_reference_node(ref_path, scope, lookups):
    if ref_path.startswith("primitive."):
        return lookups["Primitive"].get(ref_path) or lookups["Primitive"].get(f"Primitive.{ref_path}")

    return lookups[scope].get(ref_path) or lookups[scope].get(f"{scope}.{ref_path}")


def infer_token_type(path, token, scope, lookups, cache, active=None):
    cache_key = (scope, path)
    if cache_key in cache:
        return cache[cache_key]

    active = active or set()
    if cache_key in active:
        return infer_type_from_value(get_token_value(token))

    active.add(cache_key)

    explicit_type = token.get("$type") or token.get("type")
    if explicit_type:
        if explicit_type == "dimension":
            explicit_type = infer_type_from_path(path) or "number"
        cache[cache_key] = explicit_type
        active.remove(cache_key)
        return explicit_type

    path_based_type = infer_type_from_path(path)
    if path_based_type:
        cache[cache_key] = path_based_type
        active.remove(cache_key)
        return path_based_type

    raw_value = get_token_value(token)
    if is_alias(raw_value):
        ref_path = raw_value[1:-1]
        ref_node = resolve_reference_node(ref_path, scope, lookups)
        if ref_node:
            inferred = infer_token_type(ref_path, ref_node, "Primitive" if ref_path.startswith("primitive.") else scope, lookups, cache, active)
            cache[cache_key] = inferred
            active.remove(cache_key)
            return inferred

    inferred = infer_type_from_value(raw_value)
    cache[cache_key] = inferred
    active.remove(cache_key)
    return inferred


def normalize_tree(obj, prefix, scope, lookups, cache):
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
            token["$value"] = get_token_value(token)
            token.pop("value", None)
            token.setdefault("$description", "")
            token["$type"] = infer_token_type(path, token, scope, lookups, cache)
            normalized[key] = token
        elif isinstance(value, dict):
            normalized[key] = normalize_tree(value, path, scope, lookups, cache)
        else:
            normalized[key] = copy.deepcopy(value)

    return normalized


def build_adaptive_payload(source_data):
    lookups = build_lookup_tables(source_data)
    cache = {}

    payload = {}
    payload["Primitive"] = normalize_tree(source_data.get("Primitive", {}), "", "Primitive", lookups, cache)
    payload["Light"] = normalize_tree(source_data.get("Light", {}), "", "Light", lookups, cache)
    payload["Dark"] = normalize_tree(source_data.get("Dark", {}), "", "Dark", lookups, cache)

    if "$themes" in source_data:
        payload["$themes"] = copy.deepcopy(source_data["$themes"])
    if "$metadata" in source_data:
        payload["$metadata"] = copy.deepcopy(source_data["$metadata"])

    return payload


def main():
    with open("source/tokens.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    adaptive = build_adaptive_payload(data)

    os.makedirs("adapters/figma", exist_ok=True)
    out_path = "adapters/figma/figma_tokens_adaptive.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(adaptive, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✅ Generated Figma adaptive token format at: {out_path}")


if __name__ == "__main__":
    main()
