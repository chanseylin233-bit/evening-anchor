import re

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find TASK_LIBRARY array
match = re.search(r'const TASK_LIBRARY = \[(.+?)\];', content, re.DOTALL)
if not match:
    print("TASK_LIBRARY not found!")
    exit()

raw = match.group(1)
tasks = []
i = 0
while i < len(raw):
    if raw[i:i+2] == '//':
        nl = raw.find('\n', i)
        i = nl + 1 if nl != -1 else len(raw)
        continue
    if raw[i] == '{':
        depth = 0
        start = i
        for j in range(i, len(raw)):
            if raw[j] == '{': depth += 1
            elif raw[j] == '}':
                depth -= 1
                if depth == 0:
                    obj_str = raw[start:j+1]
                    cat_m = re.search(r"cat:\s*'([^']+)'", obj_str)
                    icon_m = re.search(r"icon:\s*'([^']+)'", obj_str)
                    action_m = re.search(r"action:\s*'([^']+)'", obj_str)
                    dur_m = re.search(r"dur:\s*(\d+)", obj_str)
                    energy_m = re.search(r"energy:\s*'([^']+)'", obj_str)
                    desc_m = re.search(r"desc:\s*'([^']+)'", obj_str)
                    if cat_m and icon_m and action_m:
                        tasks.append({
                            'cat': cat_m.group(1),
                            'icon': icon_m.group(1),
                            'action': action_m.group(1),
                            'dur': int(dur_m.group(1)) if dur_m else None,
                            'energy': energy_m.group(1) if energy_m else None,
                            'desc': desc_m.group(1) if desc_m else '',
                        })
                    i = j + 1
                    break
    else:
        i += 1

print(f"Total task objects: {len(tasks)}")

# 1. Exact duplicates
seen = {}
dups = []
for t in tasks:
    key = (t['cat'], t['icon'], t['action'])
    if key in seen:
        dups.append(t)
    else:
        seen[key] = t

print(f"\n=== Exact duplicates (same cat+icon+action): {len(dups)} ===")
for d in dups:
    print(f"  [{d['cat']}] {d['icon']} {d['action']} | dur={d['dur']} energy={d['energy']}")

# 2. Category+action duplicates (different icons in same cat)
print(f"\n=== cat+action duplicates (different icons): ===")
seen2 = {}
for t in tasks:
    key = (t['cat'], t['action'])
    if key not in seen2:
        seen2[key] = []
    seen2[key].append(t)

for key, items in seen2.items():
    if len(items) > 1:
        icons = [x['icon'] for x in items]
        print(f"  [{key[0]}] '{key[1]}'")
        print(f"    Icons: {icons}")
        for x in items:
            print(f"    {x['icon']} dur={x['dur']} desc={x['desc'][:30]}...")

# 3. Category counts
print(f"\n=== Category counts ===")
cats = {}
for t in tasks:
    cats[t['cat']] = cats.get(t['cat'], 0) + 1
for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {cnt}")

# 4. Show first occurrence of each unique task (sorted by cat)
print(f"\n=== All unique tasks ({len(seen)} unique) ===")
for cat in sorted(seen.keys()):
    print(f"  [{cat}] {seen[cat]['icon']} {seen[cat]['action']}")