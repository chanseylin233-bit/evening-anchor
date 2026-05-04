import re
from collections import Counter

with open('E:/projects/evening-anchor/index.html', encoding='utf-8') as f:
    content = f.read()

print(f'File size: {len(content)} chars / {content.count(chr(10))+1} lines\n')

# 1. Find duplicate function definitions
func_pattern = re.compile(r'function\s+(\w+)\s*\(')
all_funcs = [(m.start(), m.group(1)) for m in func_pattern.finditer(content)]
seen = {}
for pos, name in all_funcs:
    seen.setdefault(name, []).append(pos)

print('=== DUPLICATE FUNCTIONS ===')
for name, positions in seen.items():
    if len(positions) > 1:
        lines = [(content[:p].count('\n')+1) for p in positions]
        print(f'  {name}: lines {lines}')

# 2. Find TODO/FIXME
print('\n=== TODO/FIXME ===')
for m in re.finditer(r'// ?TODO|// ?FIXME|// ?XXX', content):
    line = content[:m.start()].count('\n') + 1
    print(f'  Line {line}: {m.group().strip()}')

# 3. Find console.log
print('\n=== CONSOLE.LOG ===')
for m in re.finditer(r'console\.(log|warn|error|debug)', content):
    line = content[:m.start()].count('\n') + 1
    snippet = content[max(0,m.start()-20):m.end()+50].replace('\n','↵')
    print(f'  Line {line}: {snippet[:100]}')

# 4. Analyze function lengths
print('\n=== LONG FUNCTIONS (>80 lines) ===')
func_starts = [(m.start(), m.group(1)) for m in re.finditer(r'function\s+(\w+)\s*\(', content)]
for i, (start, name) in enumerate(func_starts):
    end = func_starts[i+1][0] if i+1 < len(func_starts) else len(content)
    lines = content[start:end].count('\n')
    if lines > 80:
        print(f'  {name}: ~{lines} lines')

# 5. TASK_LIBRARY cat counts
print('\n=== TASK_LIBRARY CATEGORY COUNTS ===')
cats = re.findall(r'cat:\s*["\u2018\u2019](\w+)["\u2018\u2019]', content)
for cat, cnt in Counter(cats).most_common():
    print(f'  {cat}: {cnt}')

# 6. Repeated task entries in buildPlan
print('\n=== SUSPICIOUS REPETITION IN buildPlan ===')
plan_start = content.find('function buildPlan(')
plan_end = content.find('function buildLowPowerPlan(', plan_start)
plan = content[plan_start:plan_end]
# find all task action texts
actions = re.findall(r"makeBlock\(\d+,\s*['\"]([^'\"]+)['\"]", plan)
for action, cnt in Counter(actions).most_common(5):
    if cnt > 1:
        print(f'  DUPE "{action}": x{cnt}')

# 7. Inline style attributes
inline = len(re.findall(r'\sstyle=', content))
print(f'\n=== INLINE STYLES: {inline} ===')

# 8. Duplicate CSS variables
print('\n=== DUPLICATE CSS VARIABLE DECLARATIONS ===')
var_matches = re.findall(r'--[\w-]+:\s*[^;]+;', content)
var_names = [re.match(r'(--[\w-]+)', m.group()).group(1) for m in var_matches]
for v, cnt in Counter(var_names).most_common(3):
    if cnt > 1:
        print(f'  {v}: {cnt}')

# 9. Hardcoded magic numbers
print('\n=== MAGIC NUMBERS ===')
magic = re.findall(r'\b(\d{2,4})\b', content)
for num, cnt in Counter(magic).most_common(10):
    if cnt > 5:
        print(f'  {num}: appears {cnt} times')

# 10. Very long lines
print('\n=== LONG LINES (>300 chars) ===')
for i, line in enumerate(content.split('\n'), 1):
    if len(line) > 300:
        print(f'  Line {i}: {len(line)} chars — {line[:80]}...')
