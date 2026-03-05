import os
import json
import requests

FIGMA_PAT = os.getenv("FIGMA_PAT", "")
FILE_KEY = os.getenv("FIGMA_FILE_KEY", "DBQdb8ymhIfTPS9GmcTqaR")

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

def main():
    if not FIGMA_PAT or not FILE_KEY:
        print("❌ Error: Set FIGMA_PAT and FIGMA_FILE_KEY in your environment first.")
        return

    # 1. Load the Single Source of Truth
    with open('source/tokens.json', 'r') as f:
        data = json.load(f)

    # 2. Extract Data
    primitive_root = data.get('Primitive', {}).get('primitive', {}).get('color', {})
    primitive_flat = flatten_tokens(primitive_root, prefix="color/")
    light_flat = flatten_tokens(data.get('Light', {}).get('semantic', {}), prefix="")
    dark_flat = flatten_tokens(data.get('Dark', {}).get('semantic', {}), prefix="")

    # 3. Request existing variables to potentially avoid duplicates
    headers = {
        "X-Figma-Token": FIGMA_PAT,
        "Content-Type": "application/json"
    }
    
    # 4. We will create two massive collections in a single Figma API payload
    # See Figma REST API "Variables" documentation for the exact schema 
    
    # Creating variables API payload
    # NOTE: The Figma REST API POST /v1/files/:file_key/variables request structure
    # is extremely specific and strictly typed. 
    # For a robust implementation, we compile actions: CREATE_VARIABLE_COLLECTION, CREATE_VARIABLE, etc.
    
    actions = []
    
    # We will generate temporary local IDs for collections and variables 
    # so we can reference them in the same payload.
    temp_primitive_col_id = "temp_col_primitive"
    temp_semantic_col_id = "temp_col_semantic"
    
    # Create Primitive Collection Action
    actions.append({
        "action": "CREATE_VARIABLE_COLLECTION",
        "id": temp_primitive_col_id,
        "name": "Primitive",
        "initialModeId": "mode_default"
    })
    
    # Create Semantic Collection Action with Light and Dark modes
    actions.append({
        "action": "CREATE_VARIABLE_COLLECTION",
        "id": temp_semantic_col_id,
        "name": "Semantic",
        "initialModeId": "mode_light"
    })
    
    actions.append({
        "action": "ADD_MODE_TO_VARIABLE_COLLECTION",
        "variableCollectionId": temp_semantic_col_id,
        "id": "mode_dark",
        "name": "Dark"
    })
    
    actions.append({
        "action": "RENAME_VARIABLE_MODE",
        "variableCollectionId": temp_semantic_col_id,
        "id": "mode_light",
        "name": "Light"
    })

    # --- Let's add all the primitive color variables and their values ---
    primitive_id_map = {}
    
    def hex_to_rgb(hex_str, alpha=1.0):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            return {"r": r/255, "g": g/255, "b": b/255, "a": alpha}
        return {"r": 1, "g": 1, "b": 1, "a": 1} # Fallback
        
    def parse_rgba(rgba_str):
        import re
        match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', rgba_str)
        if match:
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            a = float(match.group(4)) if match.group(4) else 1.0
            return {"r": r/255, "g": g/255, "b": b/255, "a": a}
        return {"r": 1, "g": 1, "b": 1, "a": 1}

    # Creating Primitive Variables
    for identifier, value in primitive_flat.items():
        var_id = f"temp_var_prim_{identifier.replace('/', '_')}"
        primitive_id_map[identifier] = var_id
        
        actions.append({
            "action": "CREATE_VARIABLE",
            "id": var_id,
            "variableCollectionId": temp_primitive_col_id,
            "name": identifier,
            "resolvedType": "COLOR"
        })
        
        # Parse value type (Hex vs RGBA)
        if str(value).startswith("#"):
            figma_color = hex_to_rgb(str(value))
        else:
            figma_color = parse_rgba(str(value))
            
        actions.append({
            "action": "SET_VARIABLE_MODE_VALUE",
            "variableId": var_id,
            "modeId": "mode_default",
            "value": figma_color
        })

    # Creating Semantic Variables (Aliasing back to primitives!)
    all_semantic_keys = set(list(light_flat.keys()) + list(dark_flat.keys()))
    
    for identifier in all_semantic_keys:
        var_id = f"temp_var_sem_{identifier.replace('/', '_')}"
        
        actions.append({
            "action": "CREATE_VARIABLE",
            "id": var_id,
            "variableCollectionId": temp_semantic_col_id,
            "name": identifier,
            "resolvedType": "COLOR"
        })
        
        val_light = light_flat.get(identifier, "")
        val_dark = dark_flat.get(identifier, "")
        
        def extract_primitive_id(alias_str):
            if alias_str and alias_str.startswith('{') and alias_str.endswith('}'):
                inner = alias_str[1:-1]
                if inner.startswith('primitive.'):
                    inner = inner.replace('primitive.', '', 1)
                # Now it looks like color.navy.900, replace with slashes to match format
                inner = "color/" + inner.replace('.', '/').replace('color/', '')
                
                # Look up the ID in our map
                if inner in primitive_id_map:
                    return primitive_id_map[inner]
            return None

        # Bind Light Mode Alias
        light_target_id = extract_primitive_id(val_light)
        if light_target_id:
            actions.append({
                "action": "SET_VARIABLE_MODE_VALUE",
                "variableId": var_id,
                "modeId": "mode_light",
                "value": {
                    "type": "VARIABLE_ALIAS",
                    "id": light_target_id
                }
            })
            
        # Bind Dark Mode Alias
        dark_target_id = extract_primitive_id(val_dark)
        if dark_target_id:
            actions.append({
                "action": "SET_VARIABLE_MODE_VALUE",
                "variableId": var_id,
                "modeId": "mode_dark",
                "value": {
                    "type": "VARIABLE_ALIAS",
                    "id": dark_target_id
                }
            })

    payload = {
        "updateVariables": actions
    }
    
    print(f"🚀 Pushing {len(actions)} massive API actions to Figma Document: {FILE_KEY}...")
    
    endpoint = f"https://api.figma.com/v1/files/{FILE_KEY}/variables"
    response = requests.post(endpoint, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ SUCCESS! Figma Variables have been magically generated via true native API.")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ FAILED. Status Code: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    main()
