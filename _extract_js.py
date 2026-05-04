import re

with open(r'E:\projects\evening-anchor\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract main inline script (the one with const state = {, not the CDN or SW)
scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
print(f'Scripts found: {len(scripts)}')
for i, s in enumerate(scripts):
    first_line = s.strip().split('\n')[0][:80]
    print(f'  [{i}]: {first_line}')

# Find the one with 'const state'
for i, s in enumerate(scripts):
    if 'const state' in s:
        print(f'\nMain script is [{i}]')
        with open(r'E:\projects\evening-anchor\_main_js.js', 'w', encoding='utf-8') as f:
            f.write(s)
        print('Extracted to _main_js.js')
        break
