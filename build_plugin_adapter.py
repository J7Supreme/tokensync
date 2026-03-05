import json
import os

def flatten_tokens(token_dict, prefix=""):
    flat_tokens = {}
    for key, value in token_dict.items():
        if isinstance(value, dict) and ('value' in value or '$value' in value):
            token_name = f"{prefix}{key}"
            val = value.get('value') or value.get('$value')
            flat_tokens[token_name] = val
        elif isinstance(value, dict):
            new_prefix = f"{prefix}{key}/"
            flat_tokens.update(flatten_tokens(value, new_prefix))
    return flat_tokens

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return [r/255, g/255, b/255]
    return [1, 1, 1]

def parse_rgba(rgba_str):
    import re
    match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', rgba_str)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        a = float(match.group(4)) if match.group(4) else 1.0
        return [r/255, g/255, b/255], a
    return [1, 1, 1], 1.0
    
def build_color_value(value_str):
    if value_str and value_str.startswith('{') and value_str.endswith('}'):
        inner = value_str[1:-1]
        
        # We need to map {primitive.color.white} -> {Primitive/color/white}
        # Notice we use a SLASH after Primitive, not a dot!
        if inner.startswith('primitive.color.'):
            resolved = "Primitive/" + "color/" + inner.replace('primitive.color.', '', 1).replace('.', '/')
            return "{" + resolved + "}"
        elif inner.startswith('primitive.'):
            resolved = "Primitive/" + inner.replace('primitive.', '', 1).replace('.', '/')
            return "{" + resolved + "}"
        
        return "{" + inner.replace('.', '/') + "}"
        
    if value_str.startswith('#'):
        components = hex_to_rgb(value_str)
        return {
            "colorSpace": "srgb",
            "components": components,
            "alpha": 1.0,
            "hex": value_str
        }
    else:
        components, alpha = parse_rgba(value_str)
        return {
            "colorSpace": "srgb",
            "components": components,
            "alpha": alpha,
            "hex": value_str 
        }

def create_mode_file(name, flat_dict, is_primitive=False):
    output = {}
    for token_name, token_val in flat_dict.items():
        parts = token_name.split('/')
        current_level = output
        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
            
        final_key = parts[-1]
        current_level[final_key] = {
            "$type": "color",
            "$value": build_color_value(str(token_val)),
            "$extensions": {
                "com.figma.scopes": ["ALL_SCOPES"],
                "com.figma.isOverride": True
            }
        }
        
    output["$extensions"] = {
        "com.figma.modeName": name
    }
    return output


def main():
    with open('source/tokens.json', 'r') as f:
        data = json.load(f)

    primitive_root = data.get('Primitive', {}).get('primitive', {}).get('color', {})
    primitive_flat = flatten_tokens(primitive_root, prefix="color/")
    light_flat = flatten_tokens(data.get('Light', {}).get('semantic', {}), prefix="")
    dark_flat = flatten_tokens(data.get('Dark', {}).get('semantic', {}), prefix="")

    primitive_mode = create_mode_file("Default", primitive_flat, is_primitive=True)
    light_mode = create_mode_file("Light", light_flat)
    dark_mode = create_mode_file("Dark", dark_flat)

    os.makedirs('adapters/figma_plugin', exist_ok=True)
    
    with open('adapters/figma_plugin/Primitive.json', 'w') as f:
        json.dump(primitive_mode, f, indent=2, ensure_ascii=False)
        
    with open('adapters/figma_plugin/Semantic_Light.json', 'w') as f:
        json.dump(light_mode, f, indent=2, ensure_ascii=False)

    with open('adapters/figma_plugin/Semantic_Dark.json', 'w') as f:
        json.dump(dark_mode, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Generated 3 files for the 'Variables Import' plugin in 'adapters/figma_plugin/'")

if __name__ == '__main__':
    main()
