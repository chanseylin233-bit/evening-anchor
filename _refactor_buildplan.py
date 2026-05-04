#!/usr/bin/env python3
"""Refactor buildPlan: extract shared makeBlock + replace cursorMins with cursor.val"""

import re

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Build the replacement for buildPlan ──────────────────────────────
# We'll find the function body and replace it entirely.

# The old cursor block (before toTimeStr)
old_cursor_block = """    let cursorMins = 0; // minutes since arrival (relative)
    
    const toTimeStr = (offsetMins) => {
      const absMins = (arrivalMins + offsetMins) % (24 * 60);
      const h = Math.floor(absMins / 60);
      const m = absMins % 60;
      return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
    };
    
    const elapsedSinceArrival = () => cursorMins;
    const remainingUntilSleep = () => totalAvail - cursorMins;

    const isLow = energy === 'low';
    const isHigh = energy === 'high';
    const isMid = energy === 'mid';
    const hasTomorrow = tomorrow === 'has';
    
    function makeBlock(dur, icon, action, type, tag, desc, extra = {}) {
      if (cursorMins + dur > totalAvail) {
        dur = totalAvail - cursorMins;
        if (dur < 5) return null;
      }
      const start = toTimeStr(cursorMins);
      cursorMins += dur;
      const end = toTimeStr(cursorMins);
      return {
        time: { start, end },
        icon, action, type, tag, desc,
        ...extra
      };
    }"""

new_cursor_block = """    const cursor = { val: 0 }; // mutable cursor (minutes since arrival)
    
    const toTimeStr = (offsetMins) => {
      const absMins = (arrivalMins + offsetMins) % (24 * 60);
      const h = Math.floor(absMins / 60);
      const m = absMins % 60;
      return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
    };
    
    const remainingUntilSleep = () => totalAvail - cursor.val;

    const isLow = energy === 'low';
    const isHigh = energy === 'high';
    const isMid = energy === 'mid';
    const hasTomorrow = tomorrow === 'has';"""

# Helper: transform a makeBlock call line
def transform_makeblock(line):
    """Convert local makeBlock calls to shared function calls."""
    # Pattern: b = makeBlock(...) or let b = makeBlock(...)
    # Transform to: makeBlock(blocks, cursor, totalAvail, toTimeStr, ...)
    
    # Match: let b = makeBlock(...) or b = makeBlock(...)
    m = re.match(r'(\s*(?:let\s+)?b\s*=\s*makeBlock\()', line)
    if not m:
        # Also handle standalone makeBlock(...) inside if
        m = re.match(r'(\s*makeBlock\()', line)
        if not m:
            return line
    
    prefix = m.group(1)
    # Extract the arguments (everything after the opening makeBlock()
    # We need to find the matching closing paren
    paren_depth = 0
    start = line.index('makeBlock(') + len('makeBlock(')
    args_end = -1
    for i, ch in enumerate(line[start:], start):
        if ch == '(':
            paren_depth += 1
        elif ch == ')':
            if paren_depth == 0:
                args_end = i
                break
            paren_depth -= 1
    
    if args_end == -1:
        return line  # couldn't parse
    
    args = line[start:args_end]
    new_call = f"{prefix}blocks, cursor, totalAvail, toTimeStr, {args})"
    
    # Also remove the trailing if (b) blocks.push(b); pattern
    result = line[:m.start()] + new_call
    
    # Check if there's a trailing ";\n        if (b) blocks.push(b);" pattern
    return result

# ── 2. Replace cursorMins with cursor.val in the function body ──────────
# We need to be surgical: only replace cursorMins within buildPlan
# Strategy: find buildPlan function bounds and do replacements within

func_start = content.index('  function buildPlan(')
func_end = content.index('  /* ─── LOW POWER PLAN ─── */', func_start)
func_body = content[func_start:func_end]

# Step 1: replace the cursor/toTimeStr/makeBlock block
assert old_cursor_block in func_body, "cursor block not found!"
func_body = func_body.replace(old_cursor_block, new_cursor_block)

# Step 2: replace remainingUntilSleep() with totalAvail - cursor.val
# But NOT if it appears inside a makeBlock argument (those are durations, not time checks)
# Actually, remainingUntilSleep() is only used as a guard in the goal branches
func_body = re.sub(r'remainingUntilSleep\(\)', 'totalAvail - cursor.val', func_body)

# Step 3: replace direct cursorMins references (NOT inside strings)
# cursorMins++ appears as "cursorMins += dur" inside the OLD makeBlock - already removed
# Check for any remaining cursorMins
remaining_cm = re.findall(r'cursorMins', func_body)
print(f"Remaining cursorMins in buildPlan: {remaining_cm}")

# Step 4: transform all makeBlock calls
lines = func_body.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Check if this line starts a makeBlock call that spans multiple lines
    # makeBlock( can be on its own line (multi-line args)
    if re.search(r'(?:let\s+b\s*=\s*|b\s*=\s*)?makeBlock\s*\(', line):
        # Check if the call is complete on this line
        paren_count = line.count('(') - line.count(')')
        if paren_count <= 0:
            # Complete on this line
            new_line = transform_makeblock(line)
            new_lines.append(new_line)
            i += 1
            continue
        else:
            # Multi-line: collect all lines until balanced
            collected = [line]
            depth = paren_count
            j = i + 1
            while j < len(lines) and depth > 0:
                l = lines[j]
                collected.append(l)
                depth += l.count('(') - l.count(')')
                j += 1
            full_call = '\n'.join(collected)
            transformed = transform_makeblock(full_call)
            new_lines.append(transformed)
            i = j
            continue
    else:
        new_lines.append(line)
    i += 1

new_func_body = '\n'.join(new_lines)

# Step 5: Now transform individual makeBlock results
# We need: let b = makeBlock(...) → b = makeBlock(...) 
# and: if (b) blocks.push(b) → (remove, already pushed)
# The transform_makeblock already removes "let b = " prefix, 
# but we still need to handle the "if (b) blocks.push(b);" on next line

# Wait, looking at the pattern more carefully:
# Pattern A: `let b = makeBlock(...);` + next line `if (b) blocks.push(b);`
# Pattern B: `b = makeBlock(...);` + next line `if (b) blocks.push(b);`
# Pattern C: standalone `b = makeBlock(...);` (no if/push, already handled)

# Let me look at the actual patterns in the code:
# Line: "    let b = makeBlock(5, '👋', ..." 
# Next line: "    if (b) blocks.push(b);"
# or:
# Line: "        b = makeBlock(dur, '🔥', primary, ...,"
# Next line: "        if (b) blocks.push(b);"
# or multi-line with args

# The simplest approach: after making the single-line transformation,
# also remove the "if (b) blocks.push(b);" that immediately follows

final_lines = []
j = 0
while j < len(new_lines):
    line = new_lines[j]
    # Check if this line is a makeBlock call result (no "let b = ", no "if (b)")
    # and next line is "if (b) blocks.push(b);"
    if j + 1 < len(new_lines):
        next_line = new_lines[j + 1]
        # Skip the "if (b) blocks.push(b);" if the current line already pushes
        if (next_line.strip() == 'if (b) blocks.push(b);' or 
            next_line.strip() == 'if (b) blocks.push(b);'):
            # Check if current line has makeBlock result
            if 'blocks, cursor' in line and ')' in line:
                final_lines.append(line)
                j += 2  # skip the if push
                continue
    final_lines.append(line)
    j += 1

new_func_body = '\n'.join(final_lines)

# Verify
remaining = re.findall(r'cursorMins', new_func_body)
print(f"After transform - remaining cursorMins: {remaining}")
remaining2 = re.findall(r'elapsedSinceArrival', new_func_body)
print(f"After transform - remaining elapsedSinceArrival: {remaining2}")

# Check makeBlock calls are using shared function
mb_calls = re.findall(r'makeBlock\s*\(', new_func_body)
print(f"makeBlock calls (should be shared, no local def): {len(mb_calls)}")

# Now replace in content
content = content[:func_start] + new_func_body + content[func_end:]

# ── 3. Replace buildLowPowerPlan's makeBlock ──────────────────────────
lp_start = content.index('  function buildLowPowerPlan(')
lp_end = content.index('\n  /* ─── TAG CLASS ─── */', lp_start)
lp_body = content[lp_start:lp_end]

# Old: let cursorMins = 0; const toTimeStr=...; const remainingUntilSleep=...; function makeBlock(...)
old_lp_cursor = """    let cursorMins = 0;

    const toTimeStr = (offsetMins) => {
      const absMins = (arrivalMins + offsetMins) % (24 * 60);
      const h = Math.floor(absMins / 60);
      const m = absMins % 60;
      return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
    };

    const remainingUntilSleep = () => totalAvail - cursorMins;

    function makeBlock(dur, action, note) {
      if (cursorMins + dur > totalAvail) {
        dur = totalAvail - cursorMins;
        if (dur < 5) return null;
      }
      const start = toTimeStr(cursorMins);
      cursorMins += dur;
      const end = toTimeStr(cursorMins);
      return { time: { start, end }, action, note };
    }

    let b;
    b = makeBlock(5, '换衣服、坐下', '不需要做任何事，只是换好衣服');
    if (b) blocks.push(b);

    b = makeBlock(20, '简单吃点东西', '热一碗汤、吃点水果，不要勉强做饭');
    if (b) blocks.push(b);

    b = makeBlock(30, '躺着或坐着，随便干什么', '看手机、听歌、什么都不干都行');
    if (b) blocks.push(b);

    b = makeBlock(15, '简单洗漱', '刷牙、洗脸就够了');
    if (b) blocks.push(b);

    const remaining = remainingUntilSleep();"""

new_lp_cursor = """    const cursor = { val: 0 };

    const toTimeStr = (offsetMins) => {
      const absMins = (arrivalMins + offsetMins) % (24 * 60);
      const h = Math.floor(absMins / 60);
      const m = absMins % 60;
      return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
    };

    const remaining = totalAvail - cursor.val;

    makeBlockLow(blocks, cursor, totalAvail, toTimeStr, 5, '换衣服、坐下', '不需要做任何事，只是换好衣服');
    makeBlockLow(blocks, cursor, totalAvail, toTimeStr, 20, '简单吃点东西', '热一碗汤、吃点水果，不要勉强做饭');
    makeBlockLow(blocks, cursor, totalAvail, toTimeStr, 30, '躺着或坐着，随便干什么', '看手机、听歌、什么都不干都行');
    makeBlockLow(blocks, cursor, totalAvail, toTimeStr, 15, '简单洗漱', '刷牙、洗脸就够了');"""

assert old_lp_cursor in lp_body, "buildLowPowerPlan cursor block not found!"
lp_body = lp_body.replace(old_lp_cursor, new_lp_cursor)

# Also fix remaining = remainingUntilSleep() in LP plan (already done above)
# Check for remaining cursorMins in LP
remaining_lp = re.findall(r'cursorMins', lp_body)
print(f"Remaining cursorMins in LP: {remaining_lp}")

content = content[:lp_start] + lp_body + content[lp_end:]

# Write back
with open('E:/projects/evening-anchor/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
