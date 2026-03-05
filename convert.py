import json
import os

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def process_node(node):
    if isinstance(node, dict):
        if '$type' in node and node['$type'] == 'color' and '$value' in node:
            val = node['$value']
            hex_val = val.get('hex', '#000000')
            alpha = val.get('alpha', 1)
            
            # Token Studio prefers string representations for colors format
            if alpha < 1:
                r, g, b = hex_to_rgb(hex_val)
                new_val = f"rgba({r}, {g}, {b}, {round(alpha, 2)})"
            else:
                new_val = hex_val
                
            new_node = {
                "$type": "color",
                "$value": new_val
            }
            if '$description' in node:
                new_node['$description'] = node['$description']
            return new_node
        
        # Traverse dictionary
        result = {}
        for k, v in node.items():
            if k == '$extensions':  # We strip figma extensions for clean TS file
                continue
            result[k] = process_node(v)
        return result
        
    return node

def main():
    with open('token snapshot/Light.tokens.json', 'r') as f:
        light_raw = json.load(f)
        
    with open('token snapshot/Dark.tokens.json', 'r') as f:
        dark_raw = json.load(f)

    # Convert format
    light_tokens = process_node(light_raw)
    dark_tokens = process_node(dark_raw)
    
    # Token structure for Token Studio
    # According to PRD, we store it in source/tokens.json as Single Source of Truth
    ts_json = {
        "Light": light_tokens,
        "Dark": dark_tokens,
        "$themes": [
            {
                "id": "light",
                "name": "Light Theme",
                "selectedTokenSets": {
                    "Light": "enabled"
                }
            },
            {
                "id": "dark",
                "name": "Dark Theme",
                "selectedTokenSets": {
                    "Dark": "enabled"
                }
            }
        ],
        "$metadata": {
            "tokenSetOrder": [
                "Light",
                "Dark"
            ]
        }
    }
    
    os.makedirs('source', exist_ok=True)
    with open('source/tokens.json', 'w') as f:
        json.dump(ts_json, f, indent=2, ensure_ascii=False)
        
    print("Tokens successfully converted to source/tokens.json")

if __name__ == '__main__':
    main()
