import re
from collections import Counter

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print('=== CODE REVIEW ===\n')

# 1. Unused variables
declared_vars = {}
used_vars = set()

for i, line in enumerate(lines, 1):
    for m in re.finditer(r'\b(let|const|var)\s+(\w+)', line):
        declared_vars[m.group(2)] = i
    
    for var in list(declared_vars.keys()):
        if var in line and f'let {var}' not in line and f'const {var}' not in line and f'var {var}' not in line:
            used_vars.add(var)

unused = set(declared_vars.keys()) - used_vars
# Filter false positives
false_positives = ['state', 'TASK_LIBRARY', 'GOAL_PLAN_CONFIG', 'b', 'blocks', 'cursor', 'usedIdx', 
                   'escapeHtml', 'parseTimeHM', 'addMinutes', 'formatTime', 'estimateDuration',
                   'tagClass', 'pickTasks', 'makeBlock', 'makeBlockLow', 'buildPlan', 'buildLowPowerPlan',
                   'generatePlan', 'renderPlan', 'updateProgress', 'copyPlan', 'exportImage',
                   'initWheelCss', 'bindWheelPickers', '_buildScroll', 'openWheel', 'closeWheel', '_onScroll',
                   'registerServiceWorker', '_toTimeStr', '_makeBlock', 'addGoalBlocks', 'addBuffer']
unused = [v for v in unused if v not in false_positives and not v.startswith('_')]

if unused:
    print('Potentially unused variables:')
    for v in sorted(unused):
        print(f'  {v} (line {declared_vars[v]})')
else:
    print('No obvious unused variables found')

# 2. Duplicate function definitions
func_defs = {}
for i, line in enumerate(lines, 1):
    m = re.search(r'\bfunction\s+(\w+)\s*\(', line)
    if m:
        name = m.group(1)
        if name in func_defs:
            print(f'Duplicate function: {name} at lines {func_defs[name]} and {i}')
        func_defs[name] = i

# 3. Long inline styles
long_styles = []
for i, line in enumerate(lines, 1):
    styles = re.findall(r'style="([^"]{30,})"', line)
    if styles:
        long_styles.append((i, len(styles[0])))

if long_styles:
    print(f'\nLong inline styles (>30 chars): {len(long_styles)} instances')
    for line, length in long_styles[:5]:
        print(f'  Line {line}: {length} chars')

# 4. console.log and debugger
console_logs = len(re.findall(r'console\.log\(', content))
debuggers = len(re.findall(r'\bdebugger\b', content))
print(f'\nconsole.log: {console_logs}, debugger: {debuggers}')

# 5. Repeated colors
colors = re.findall(r'#[0-9A-Fa-f]{6}', content)
color_counts = Counter(colors)
repeated_colors = [(c, n) for c, n in color_counts.items() if n >= 5]
if repeated_colors:
    print(f'\nRepeated colors (>=5 times):')
    for color, count in sorted(repeated_colors, key=lambda x: -x[1]):
        print(f'  {color}: {count}x')

print(f'\nTotal lines: {len(lines)}')
