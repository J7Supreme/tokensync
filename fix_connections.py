import json
import re

# Semantic Map from transform.py
MAP = {
    "Bg Fill": {
        "General": ["semantic", "background", "general"],
        "Card": ["semantic", "background", "card"],
        "Modal": ["semantic", "background", "modal"],
        "Section in modal": ["semantic", "background", "modal_section"],
        "In section in a modal": ["semantic", "background", "modal_section_inner"]
    },
    "Text": {
        "Core": ["semantic", "text", "core"],
        "Primary": ["semantic", "text", "primary"],
        "Secondary": ["semantic", "text", "secondary"],
        "Link or button": ["semantic", "text", "action"],
        "Placeholder": ["semantic", "text", "placeholder"]
    },
    "Stoke": {
        "Icon stroke": ["semantic", "stroke", "icon_primary"],
        "Icon stroke secondary": ["semantic", "stroke", "icon_secondary"],
        "Boarder": ["semantic", "border", "default"]
    },
    "Fill": {
        "Icon,Chip": ["semantic", "fill", "icon_chip"],
        "Fill B": ["semantic", "fill", "secondary"],
        "Fill C": ["semantic", "fill", "tertiary"],
        "Modal backdrop": ["semantic", "background", "backdrop"],
        "Logo": ["semantic", "fill", "logo"],
        "Color": ["semantic", "fill", "color_1"],
        "Color 2": ["semantic", "fill", "color_2"]
    },
    "*For linear gradient use": {
        "General bkg linear-1": ["semantic", "gradient", "general_1"],
        "General bkg linear-2": ["semantic", "gradient", "general_2"],
        "Token main bkg linear-1": ["semantic", "gradient", "main_1"],
        "Token main bkg linear-2": ["semantic", "gradient", "main_2"],
        "XAUT CARD BKG Linear -1": ["semantic", "gradient", "xaut_card_1"],
        "XAUT CARD BKG Linear - 2": ["semantic", "gradient", "xaut_card_2"],
        "Bar backdrop linear-1": ["semantic", "gradient", "bar_backdrop_1"],
        "Bar backdrop linear-2": ["semantic", "gradient", "bar_backdrop_2"]
    }
}

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

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def process_node(node):
    if isinstance(node, dict):
        if '$type' in node and node['$type'] == 'color' and '$value' in node:
            val = node['$value']
            hex_val = val.get('hex', '#000000')
            alpha = val.get('alpha', 1)
            
            if alpha < 1:
                r, g, b = hex_to_rgb(hex_val)
                new_val = f"rgba({r}, {g}, {b}, {round(alpha, 2)})"
            else:
                new_val = hex_val.upper()
                
            new_node = {
                "$type": "color",
                "$value": new_val
            }
            if '$description' in node:
                new_node['$description'] = node['$description']
            return new_node
        
        result = {}
        for k, v in node.items():
            if k == '$extensions':
                continue
            result[k] = process_node(v)
        return result
        
    return node

def set_nested(d, path, value):
    for key in path[:-1]:
        d = d.setdefault(key, {})
    d[path[-1]] = value

def generate_primitive_name(val):
    val = val.upper() if val.startswith('#') else val
    if val in COLOR_MAP:
        return COLOR_MAP[val]
    
    m = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)', val)
    if m:
        r, g, b, a = m.groups()
        r, g, b = int(r), int(g), int(b)
        base_hex = f"#{r:02X}{g:02X}{b:02X}"
        base_name = COLOR_MAP.get(base_hex, f"custom_{r}_{g}_{b}")
        alpha_perc = int(float(a) * 100)
        # Fix for DTCG syntax: Don't use dot for alpha so it doesn't create nested object
        return f"{base_name}_a{alpha_perc}"
    
    return "custom_" + val.replace('#', '')

def apply_semantic_map(theme_data):
    new_theme = {}
    for group, items in theme_data.items():
        if group in MAP:
            for item_key, current_val in items.items():
                if item_key in MAP[group]:
                    path = MAP[group][item_key]
                    set_nested(new_theme, path, current_val)
                else:
                    set_nested(new_theme, ["semantic", "unmapped", item_key], current_val)
        else:
             new_theme[group] = items
    return new_theme

primitives_flat = {}

def extract_and_link_primitives(theme_data):
    if not isinstance(theme_data, dict):
        return theme_data
        
    if "$type" in theme_data and theme_data["$type"] == "color":
        val = theme_data["$value"]
        prim_name = generate_primitive_name(val)
        if prim_name not in primitives_flat:
            primitives_flat[prim_name] = val
        
        # In Tokens Studio, we can reference by {set.token} or {token}. Usually omitting set for flat resolution.
        # But if root is "primitive", it should be "{primitive.color.name}"
        res = {
            "$type": "color",
            "$value": f"{{primitive.color.{prim_name}}}"
        }
        if "$description" in theme_data:
            res["$description"] = theme_data["$description"]
        return res
        
    new_dict = {}
    for k, v in theme_data.items():
        new_dict[k] = extract_and_link_primitives(v)
    return new_dict

def main():
    with open('token snapshot/Light.tokens.json', 'r') as f:
        light_raw = json.load(f)
    with open('token snapshot/Dark.tokens.json', 'r') as f:
        dark_raw = json.load(f)

    # 1. Clean up figma extensions and normalize values
    light_clean = process_node(light_raw)
    dark_clean = process_node(dark_raw)

    # 2. Map structural names
    light_sem = apply_semantic_map(light_clean)
    dark_sem = apply_semantic_map(dark_clean)

    # 3. Extract primitives and link
    light_linked = extract_and_link_primitives(light_sem)
    dark_linked = extract_and_link_primitives(dark_sem)

    # 4. Build primitive set
    primitive_set = {}
    for p_name, p_val in primitives_flat.items():
        path = ["primitive", "color"] + p_name.split('.')
        set_nested(primitive_set, path, {
            "$type": "color",
            "$value": p_val
        })
        
    ts_json = {
        "Primitive": primitive_set,
        "Light": light_linked,
        "Dark": dark_linked,
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
    print("Fixed DTCG primitive structure to resolve Token Studio connection drop.")

if __name__ == '__main__':
    main()
