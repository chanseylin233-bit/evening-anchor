#!/usr/bin/env python3
"""Refactor buildPlan and buildLowPowerPlan: extract shared makeBlock."""
import re

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ═══════════════════════════════════════════════════════════════
# PART 1: Fix buildPlan
# ═══════════════════════════════════════════════════════════════
bp_start = content.index('  function buildPlan(')
bp_end   = content.index('  /* ─── LOW POWER PLAN ─── */')
bp_body  = content[bp_start:bp_end]
bp_after = content[bp_end:]

# ── 1a. Replace cursorMins vars + inline helpers ──────────────────
# Remove elapsedSinceArrival (never called)
bp_body = re.sub(
    r'\n    const elapsedSinceArrival = \(\) => cursorMins;\n',
    '\n', bp_body)

# Remove local makeBlock function definition (multiline)
bp_body = re.sub(
    r'\n    function makeBlock\(dur, icon, action, type, tag, desc, extra = \{\}\) \{.*?\n    \}\n',
    '\n', bp_body, flags=re.DOTALL)

# Replace "let cursorMins = 0" → "const cursor = { val: 0 }"
bp_body = re.sub(
    r'let cursorMins = 0; // minutes since arrival \(relative\)',
    'const cursor = { val: 0 }; // mutable cursor (minutes since arrival)',
    bp_body)

# Replace remaining "cursorMins" → "cursor.val"
bp_body = re.sub(r'\bcursorMins\b', 'cursor.val', bp_body)

# Replace remainingUntilSleep() → totalAvail - cursor.val
# (some were already converted; redo cleanly)
bp_body = re.sub(r'remainingUntilSleep\(\)', 'totalAvail - cursor.val', bp_body)

# ── 1b. Replace "const remainingUntilSleep = () => totalAvail - cursor.val;" ──
# Remove the line (no longer needed since all calls are inlined)
bp_body = re.sub(
    r'\n    const remainingUntilSleep = \(\) => totalAvail - cursor\.val;\n',
    '\n', bp_body)

# ── 1c. Transform makeBlock calls ─────────────────────────────────
# Pattern: "let b = makeBlock(...)" or "b = makeBlock(...)" or "b = makeBlock(\n"
# Transform to: "b = makeBlock(blocks, cursor, totalAvail, toTimeStr, ...)"
# And remove the trailing "if (b) blocks.push(b);"

def replace_makeblock_calls(text):
    """Transform makeBlock calls to use the shared function."""
    result = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect makeBlock call start
        m = re.match(r'^(\s*)((?:let\s+)?b\s*=\s*)?(makeBlock)\s*\(', line)
        if not m:
            result.append(line)
            i += 1
            continue

        indent = m.group(1)
        has_let = bool(m.group(2))
        # Collect the full call (might span multiple lines)
        call_lines = [line]
        paren_depth = line.count('(') - line.count(')')
        j = i + 1
        while j < len(lines) and paren_depth > 0:
            ll = lines[j]
            call_lines.append(ll)
            paren_depth += ll.count('(') - ll.count(')')
            j += 1

        full_call = '\n'.join(call_lines)
        # Extract args: find "makeBlock(" and match to closing paren
        mk_start = full_call.index('makeBlock(') + len('makeBlock(')
        # Find matching close paren
        depth = 0
        end_idx = mk_start
        for k, ch in enumerate(full_call[mk_start:], mk_start):
            if ch == '(':
                depth += 1
            elif ch == ')':
                if depth == 0:
                    end_idx = k
                    break
                depth -= 1
        args = full_call[mk_start:end_idx].strip()
        # Remove trailing semicolon
        args = args.rstrip(';').strip()

        new_call = f'{indent}b = makeBlock(blocks, cursor, totalAvail, toTimeStr, {args});'
        result.append(new_call)
        i = j

        # Skip following "if (b) blocks.push(b);" line
        if i < len(lines) and lines[i].strip() == 'if (b) blocks.push(b);':
            i += 1
            continue

    return '\n'.join(result)

bp_body = replace_makeblock_calls(bp_body)

# Verify buildPlan
bad = re.findall(r'\bcursorMins\b', bp_body)
print(f"[buildPlan] cursorMins remaining: {bad}")
bad2 = re.findall(r'elapsedSinceArrival', bp_body)
print(f"[buildPlan] elapsedSinceArrival remaining: {bad2}")
mb_calls = len(re.findall(r'makeBlock\s*\(', bp_body))
print(f"[buildPlan] makeBlock call sites: {mb_calls}")

# ═══════════════════════════════════════════════════════════════
# PART 2: Fix buildLowPowerPlan
# ═══════════════════════════════════════════════════════════════
lp_start = content.index('  function buildLowPowerPlan(')
lp_end   = content.index('\n  /* ─── TAG CLASS ─── */', lp_start)
lp_body  = content[lp_start:lp_end]

# Replace cursorMins vars
lp_body = re.sub(r'\blet cursorMins = 0;', 'const cursor = { val: 0 };', lp_body)
lp_body = re.sub(r'\bcursorMins\b', 'cursor.val', lp_body)

# Remove local toTimeStr + remainingUntilSleep + makeBlock
lp_body = re.sub(
    r'\n\n    const toTimeStr = \(offsetMins\) => \{.*?\n    \}\n',
    '\n', lp_body, flags=re.DOTALL)
lp_body = re.sub(
    r'\n    const remainingUntilSleep = \(\) => totalAvail - cursor\.val;\n',
    '\n', lp_body)
lp_body = re.sub(
    r'\n    function makeBlock\(dur, action, note\) \{.*?\n    \}\n',
    '\n', lp_body, flags=re.DOTALL)

# Transform b = makeBlock(...) calls to b = makeBlockLow(...)
# And remove the trailing if (b) blocks.push(b);
def replace_makeblocklow_calls(text):
    result = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(\s*)b = makeBlock\((.*)\);', line, re.DOTALL)
        if m:
            args = m.group(2).strip()
            indent = m.group(1)
            new_call = f'{indent}b = makeBlockLow(blocks, cursor, totalAvail, toTimeStr, {args});'
            result.append(new_call)
            i += 1
            if i < len(lines) and lines[i].strip() == 'if (b) blocks.push(b);':
                i += 1
                continue
        else:
            # remaining = remainingUntilSleep() → totalAvail - cursor.val
            if 'const remaining = remainingUntilSleep()' in line:
                line = re.sub(r'remainingUntilSleep\(\)', 'totalAvail - cursor.val', line)
            result.append(line)
            i += 1
    return '\n'.join(result)

lp_body = replace_makeblocklow_calls(lp_body)

bad3 = re.findall(r'\bcursorMins\b', lp_body)
print(f"[buildLowPowerPlan] cursorMins remaining: {bad3}")
bad4 = re.findall(r'function makeBlock', lp_body)
print(f"[buildLowPowerPlan] makeBlock def remaining: {bad4}")

# ═══════════════════════════════════════════════════════════════
# PART 3: Stitch back
# ═══════════════════════════════════════════════════════════════
# content was modified in-place for bp_end/lp_end indices, recalculate
with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    full = f.read()

bp_start2 = full.index('  function buildPlan(')
bp_end2   = full.index('  /* ─── LOW POWER PLAN ─── */')
lp_start2 = full.index('  function buildLowPowerPlan(')
lp_end2   = full.index('\n  /* ─── TAG CLASS ─── */', lp_start2)

new_content = (
    full[:bp_start2]
    + bp_body
    + full[bp_end2:lp_start2]
    + lp_body
    + full[lp_end2:]
)

with open('E:/projects/evening-anchor/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nTotal lines after refactor: {len(new_content.splitlines())}")
print("Done!")
