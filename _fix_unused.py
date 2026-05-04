import re

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# 1. Remove unused isMid variable (line 1658)
# Find and remove the line
new_lines = []
for i, line in enumerate(lines):
    if "const isMid = energy === 'mid';" in line:
        print(f'Removing line {i+1}: {line.strip()}')
        continue
    new_lines.append(line)

content = '\n'.join(new_lines)

# 2. Remove unused visCount variable (was line 2542, now shifted)
# Find the line in the new content
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    if 'const visCount = 4;' in line and 'wheel' in lines[i-1] if i > 0 else False:
        print(f'Removing line {i+1}: {line.strip()}')
        continue
    # Also remove the comment referencing it
    if 'Show 4 items (0..3)' in line and 'visCount' not in lines[i+2] if i+2 < len(lines) else True:
        # Check if next non-empty line defines visCount
        for j in range(i+1, min(i+5, len(lines))):
            if 'visCount' in lines[j]:
                print(f'Removing comment line {i+1}: {line.strip()}')
                break
        new_lines.append(line)
        continue
    new_lines.append(line)

content = '\n'.join(new_lines)

# Write back
with open('E:/projects/evening-anchor/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone! File size: {len(content)} bytes')
