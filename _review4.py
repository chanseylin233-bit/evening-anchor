import re

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. find all function/const defs (excluding wheel-picker CSS and HTML)
# 2. check estimateDuration SCORE for remaining dups
# 3. check for console.log / TODO / FIXME
# 4. measure key function body sizes

# Helper: find function start/end
funcs = {}
stack = []  # (name, start_line)
for i, line in enumerate(lines):
    # function declarations
    m = re.match(r'\s*(function\s+(\w+)|const\s+(\w+)\s*=|function\s+(\w+)\s*\()', line)
    if m:
        fname = m.group(2) or m.group(3) or m.group(4)
        if fname and not fname.startswith('__') and not fname.startswith('_'):
            stack.append((fname, i+1))
    # closing brace (rough)
    # We'll just collect starts and rough lengths

print("=== Functions defined (non-_) ===")
for fname, start in stack:
    print(f"  {fname}: line {start}")

print("\n=== console.log / TODO / FIXME ===")
for i, line in enumerate(lines):
    t = line.strip()
    if any(x in t for x in ['console.log', '// TODO', '// FIXME', '// DEPRECATED']):
        print(f"  {i+1}: {t[:80]}")