"""
Fix: toTimeStr was removed from buildPlan/buildLowPowerPlan but call sites still
reference the now-undefined variable `toTimeStr`.

Solution:
1. Update _makeBlock(blocks, cr, total, ts, dur) → _makeBlock(blocks, cr, total, arrivalMins, dur)
   so it calls _toTimeStr(arrivalMins, cr.val) directly (no ts param needed).
2. Update makeBlock / makeBlockLow signatures similarly.
3. Update all call sites: makeBlock(..., toTimeStr, ...) → makeBlock(..., arrivalMins, ...)
"""
import re

path = 'E:/projects/evening-anchor/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

orig_len = len(content)

# ── Step 1: Update _makeBlock signature + body ──
# Old: function _makeBlock(blocks, cr, total, ts, dur) {
#      const start = ts(cr.val); ... const end = ts(cr.val);
# New: function _makeBlock(blocks, cr, total, arrivalMins, dur) {
#      const start = _toTimeStr(arrivalMins, cr.val); ... const end = _toTimeStr(arrivalMins, cr.val);
content = content.replace(
    'function _makeBlock(blocks, cr, total, ts, dur)',
    'function _makeBlock(blocks, cr, total, arrivalMins, dur)'
)
content = content.replace(
    'const start = ts(cr.val);',
    'const start = _toTimeStr(arrivalMins, cr.val);'
)
content = content.replace(
    'const end = ts(cr.val);',
    'const end = _toTimeStr(arrivalMins, cr.val);'
)
print("Step1: updated _makeBlock to use arrivalMins param + _toTimeStr")

# ── Step 2: Update makeBlock signature ──
# Old: makeBlock(blocks, cr, total, ts, dur, icon, action, type, tag, desc, extra)
# New: makeBlock(blocks, cr, total, arrivalMins, dur, icon, action, type, tag, desc, extra)
content = content.replace(
    'function makeBlock(blocks, cr, total, ts, dur,',
    'function makeBlock(blocks, cr, total, arrivalMins, dur,'
)
content = content.replace(
    '    const b = _makeBlock(blocks, cr, total, ts, dur);',
    '    const b = _makeBlock(blocks, cr, total, arrivalMins, dur);'
)
print("Step2: updated makeBlock signature and _makeBlock call")

# ── Step 3: Update makeBlockLow signature ──
content = content.replace(
    'function makeBlockLow(blocks, cr, total, ts, dur, action, note)',
    'function makeBlockLow(blocks, cr, total, arrivalMins, dur, action, note)'
)
content = content.replace(
    '    const b = _makeBlock(blocks, cr, total, ts, dur);',
    '    const b = _makeBlock(blocks, cr, total, arrivalMins, dur);'
)
print("Step3: updated makeBlockLow signature and _makeBlock call")

# ── Step 4: Update all call sites ──
# Pattern: makeBlock(blocks, cursor, totalAvail, toTimeStr, ... → makeBlock(blocks, cursor, totalAvail, arrivalMins,
# Pattern: makeBlockLow(blocks, cursor, totalAvail, toTimeStr, ... → makeBlockLow(blocks, cursor, totalAvail, arrivalMins,
# The 4th argument (index 3, 0-based after the opening paren) changes from toTimeStr to arrivalMins
# Call sites look like: b = makeBlock(blocks, cursor, totalAvail, toTimeStr, 5, ...
# We need: b = makeBlock(blocks, cursor, totalAvail, arrivalMins, 5, ...
# Also: b = makeBlockLow(blocks, cursor, totalAvail, toTimeStr, 5, ...
# We need: b = makeBlockLow(blocks, cursor, totalAvail, arrivalMins, 5, ...

content = content.replace(
    'makeBlock(blocks, cursor, totalAvail, toTimeStr,',
    'makeBlock(blocks, cursor, totalAvail, arrivalMins,'
)
content = content.replace(
    'makeBlockLow(blocks, cursor, totalAvail, toTimeStr,',
    'makeBlockLow(blocks, cursor, totalAvail, arrivalMins,'
)
print("Step4: updated all call sites (toTimeStr → arrivalMins)")

# ── Verify ──
bad_toTimeStr = [l for l in content.split('\n')
                 if 'toTimeStr' in l and 'const toTimeStr' not in l
                 and '_toTimeStr(arrivalMins' not in l]
if bad_toTimeStr:
    print(f"WARNING: remaining toTimeStr refs: {bad_toTimeStr[:5]}")
else:
    print("Verify OK: no rogue toTimeStr references")

# Count call sites with arrivalMins
calls = [l for l in content.split('\n') if 'makeBlock(blocks, cursor, totalAvail, arrivalMins,' in l
         or 'makeBlockLow(blocks, cursor, totalAvail, arrivalMins,' in l]
print(f"Call sites updated: {len(calls)}")

new_len = len(content)
print(f"Size: {orig_len} → {new_len} ({orig_len - new_len} bytes)")
print(f"Total lines: {content.count(chr(10)) + 1}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)