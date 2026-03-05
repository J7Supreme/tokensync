import json
import os

def main():
    with open('source/tokens.json', 'r') as f:
        data = json.load(f)
        
    primitive = data.get("Primitive", {})
    light = data.get("Light", {})
    dark = data.get("Dark", {})

    with open('source/primitive.json', 'w') as f:
        json.dump(primitive, f, indent=2, ensure_ascii=False)
        
    with open('source/light.json', 'w') as f:
        json.dump(light, f, indent=2, ensure_ascii=False)
        
    with open('source/dark.json', 'w') as f:
        json.dump(dark, f, indent=2, ensure_ascii=False)
        
    print("Files split.")

if __name__ == '__main__':
    main()
