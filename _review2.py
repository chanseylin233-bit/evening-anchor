import re
from collections import Counter

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print('=== PATTERN ANALYSIS ===\n')

# 1. Check for repeated SVG patterns
svg_paths = re.findall(r'd="([^"]+)"', content)
path_counts = Counter(svg_paths)
repeated_paths = [(p, n) for p, n in path_counts.items() if n >= 3]
if repeated_paths:
    print('Repeated SVG paths (>=3x):')
    for path, count in sorted(repeated_paths, key=lambda x: -x[1])[:5]:
        print(f'  {path[:50]}...: {count}x')

# 2. Check for repeated text patterns in JS
script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
js_section = script_match.group(1) if script_match else ''

# Find repeated string literals
strings = re.findall(r"'([^']{10,})'", js_section)
string_counts = Counter(strings)
repeated_strings = [(s, n) for s, n in string_counts.items() if n >= 2]
if repeated_strings:
    print(f'\nRepeated string literals (>=2x): {len(repeated_strings)}')
    for s, count in sorted(repeated_strings, key=lambda x: -x[1])[:5]:
        print(f'  "{s[:40]}...": {count}x')

# 3. Check for similar function bodies
print('\n=== FUNCTION SIZE ===')
func_starts = []
for i, line in enumerate(lines, 1):
    m = re.search(r'\bfunction\s+(\w+)\s*\(', line)
    if m:
        func_starts.append((m.group(1), i))

# Get function sizes (approximate, by indentation)
for name, start in func_starts:
    # Count lines until indentation decreases
    base_indent = len(lines[start-1]) - len(lines[start-1].lstrip())
    size = 1
    for j in range(start, min(start + 100, len(lines))):
        line = lines[j]
        if line.strip() and not line.strip().startswith('//'):
            curr_indent = len(line) - len(line.lstrip())
            if curr_indent <= base_indent and size > 1:
                break
        size += 1
    if size > 30:
        print(f'  {name}: ~{size} lines (line {start})')

print(f'\nTotal lines: {len(lines)}')
