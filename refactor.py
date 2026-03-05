import json
import re

# Color naming mapping (approximate for the given hex values)
COLOR_MAP = {
    "#FFFFFF": "white",
    "#000000": "black",
    "#F9FAFB": "gray.50",
    "#F0F1F3": "gray.100",
    "#D6D7E0": "gray.300",
    "#DDDEEA": "gray.400",
    "#1C1C1E": "gray.900",
    "#2C2C2E": "gray.800",
    "#111D4A": "navy.900",
    "#007FFF": "blue.500",
    "#F9FDFF": "blue.50",
    "#D6EBFF": "blue.100",
    "#EEF7FF": "blue.200",
    "#003160": "navy.800",
    "#1F1F1F": "gray.850",
    "#272727": "gray.800",
    "#010306": "gray.950"
}

def rgba_to_hex_alpha(rgba_str):
    # Just to handle matching or naming
    pass

def generate_primitive_name(val):
    val = val.upper() if val.startswith('#') else val
    if val in COLOR_MAP:
        return COLOR_MAP[val]
    
    # Handle rgba
    m = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)', val)
    if m:
        r, g, b, a = m.groups()
        # convert to hex to find base color
        r, g, b = int(r), int(g), int(b)
        base_hex = f"#{r:02X}{g:02X}{b:02X}"
        base_name = COLOR_MAP.get(base_hex, f"custom_{r}_{g}_{b}")
        alpha_perc = int(float(a) * 100)
        return f"{base_name}.a{alpha_perc}"
    
    return "custom_" + val.replace('#', '')

def set_nested(d, path, value):
    for key in path[:-1]:
        d = d.setdefault(key, {})
    d[path[-1]] = value

def refactor():
    with open('source/tokens.json', 'r') as f:
        data = json.load(f)

    primitives_flat = {}
    new_light = {}
    new_dark = {}

    def process_semantic(theme_name, old_data, new_data):
        # old_data has "semantic": { "background": { ... } }
        sem_data = old_data.get("semantic", {})
        for category, elements in sem_data.items():
            for element, variants in elements.items():
                if "$type" in variants: # it's a leaf
                    val = variants["$value"]
                    prim_name = generate_primitive_name(val)
                    if prim_name not in primitives_flat:
                        primitives_flat[prim_name] = val
                    
                    # Store as semantic.category.element
                    token_path = ["semantic", category, element]
                    new_token = {
                        "$type": "color",
                        "$value": f"{{primitive.color.{prim_name}}}"
                    }
                    if "$description" in variants:
                        new_token["$description"] = variants["$description"]
                    set_nested(new_data, token_path, new_token)
                else:
                    for variant, leaf in variants.items():
                        if "$type" in leaf:
                            val = leaf["$value"]
                            prim_name = generate_primitive_name(val)
                            if prim_name not in primitives_flat:
                                primitives_flat[prim_name] = val
                            
                            token_path = ["semantic", category, element, variant]
                            new_token = {
                                "$type": "color",
                                "$value": f"{{primitive.color.{prim_name}}}"
                            }
                            if "$description" in leaf:
                                new_token["$description"] = leaf["$description"]
                            set_nested(new_data, token_path, new_token)

    process_semantic("Light", data.get("Light", {}), new_light)
    process_semantic("Dark", data.get("Dark", {}), new_dark)

    primitive_set = {}
    for p_name, p_val in primitives_flat.items():
        parts = p_name.split('.')
        path = ["primitive", "color"] + parts
        set_nested(primitive_set, path, {
            "$type": "color",
            "$value": p_val
        })
        
    ts_json = {
        "Primitive": primitive_set,
        "Light": new_light,
        "Dark": new_dark,
        "$themes": [
            {
                "id": "light",
                "name": "Light Theme",
                "selectedTokenSets": {
                    "Primitive": "enabled",
                    "Light": "enabled",
                    "Dark": "disabled"
                }
            },
            {
                "id": "dark",
                "name": "Dark Theme",
                "selectedTokenSets": {
                    "Primitive": "enabled",
                    "Dark": "enabled",
                    "Light": "disabled"
                }
            }
        ],
        "$metadata": {
            "tokenSetOrder": [
                "Primitive",
                "Light",
                "Dark"
            ]
        }
    }

    with open('source/tokens.json', 'w') as f:
        json.dump(ts_json, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    refactor()
