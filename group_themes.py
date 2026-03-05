import json

def main():
    with open('source/tokens.json', 'r') as f:
        data = json.load(f)
        
    for theme in data.get('$themes', []):
        theme['group'] = 'Semantic'
        if theme['id'] == 'light':
            theme['name'] = 'Light'
        if theme['id'] == 'dark':
            theme['name'] = 'Dark'
            
    with open('source/tokens.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
