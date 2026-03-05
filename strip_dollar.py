import json

def strip_dollar_prefix(node):
    if isinstance(node, dict):
        new_dict = {}
        for k, v in node.items():
            if k in ['$themes', '$metadata']:
                new_dict[k] = v
                continue
            
            new_key = k
            if k in ['$type', '$value', '$description']:
                new_key = k[1:]
            new_dict[new_key] = strip_dollar_prefix(v)
        return new_dict
    elif isinstance(node, list):
        return [strip_dollar_prefix(item) for item in node]
    else:
        return node

def main():
    with open('source/tokens.json', 'r') as f:
        data = json.load(f)
        
    native_data = strip_dollar_prefix(data)
    
    with open('source/tokens.json', 'w') as f:
        json.dump(native_data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
