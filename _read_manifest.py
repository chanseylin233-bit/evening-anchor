import json
with open('E:/projects/evening-anchor/manifest.json', 'r', encoding='utf-8') as f:
    print(json.dumps(json.load(f), indent=2))