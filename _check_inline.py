import re

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find inline styles
print('=== INLINE STYLES (20+ chars) ===')
matches = re.finditer(r'style="([^"]{20,})"', content)
count = 0
for m in matches:
    line_num = content[:m.start()].count('\n') + 1
    print(f'Line {line_num}: {m.group(1)[:60]}...')
    count += 1

print(f'\nTotal: {count} inline styles')
