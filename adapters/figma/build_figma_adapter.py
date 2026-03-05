import json
import os

def flatten_tokens(token_dict, prefix=""):
    flat_tokens = {}
    for key, value in token_dict.items():
        if isinstance(value, dict) and ('value' in value or '$value' in value):
            # token studio format
            token_name = f"{prefix}{key}"
            val = value.get('value') or value.get('$value')
            flat_tokens[token_name] = val
        elif isinstance(value, dict):
            # It's a group
            new_prefix = f"{prefix}{key}/"
            flat_tokens.update(flatten_tokens(value, new_prefix))
    return flat_tokens

def main():
    with open('source/tokens.json', 'r') as f:
        data = json.load(f)

    # In source/tokens.json 
    # The structure is data['Primitive']['primitive']['color']
    primitive_root = data.get('Primitive', {}).get('primitive', {}).get('color', {})
    primitive_flat = flatten_tokens(primitive_root, prefix="color/")
    
    # Semantic Collection for Light and Dark
    light_root = data.get('Light', {}).get('semantic', {})
    light_flat = flatten_tokens(light_root, prefix="")
    
    dark_root = data.get('Dark', {}).get('semantic', {})
    dark_flat = flatten_tokens(dark_root, prefix="")

    collections = []

    # --- Primitive Collection ---
    primitive_vars = []
    for name, val in primitive_flat.items():
        primitive_vars.append({
            "name": name,
            "type": "COLOR",
            "valuesByMode": {
                "Default": val
            }
        })
        
    collections.append({
        "name": "Primitive",
        "modes": ["Default"],
        "variables": primitive_vars
    })

    # --- Semantic Collection ---
    semantic_vars = []
    all_semantic_keys = set(list(light_flat.keys()) + list(dark_flat.keys()))
    
    def format_alias(v):
        if v and v.startswith('{') and v.endswith('}'):
            inner = v[1:-1]
            if inner.startswith('primitive.'):
                inner = inner.replace('primitive.', '', 1)
            return "{" + inner.replace('.', '/') + "}"
        return v
            
    for name in all_semantic_keys:
        val_light = light_flat.get(name, "")
        val_dark = dark_flat.get(name, "")
        
        semantic_vars.append({
            "name": name,
            "type": "COLOR",
            "valuesByMode": {
                "Light": format_alias(val_light),
                "Dark": format_alias(val_dark)
            }
        })

    collections.append({
        "name": "Semantic",
        "modes": ["Light", "Dark"],
        "variables": semantic_vars
    })

    figma_native_json = {
        "collections": collections
    }

    os.makedirs('adapters/figma', exist_ok=True)
    out_path = 'adapters/figma/figma_variables.json'
    with open(out_path, 'w') as f:
        json.dump(figma_native_json, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Generated Figma Native Variables format at: {out_path}")

if __name__ == '__main__':
    main()
