"""
Extract shared _toTimeStr, remove duplicate definitions from buildPlan + buildLowPowerPlan.
"""
import re

path = 'E:/projects/evening-anchor/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

orig_len = len(content)

# ── Step 1: Insert shared _toTimeStr after makeBlockLow, before escapeHtml ──
shared_fn = """
  // Shared time-string formatter (avoids duplication in buildPlan / buildLowPowerPlan)
  function _toTimeStr(arrivalMins, offsetMins) {
    const absMins = (arrivalMins + offsetMins) % (24 * 60);
    const h = Math.floor(absMins / 60);
    const m = absMins % 60;
    return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
  }
"""

# find the closing } of makeBlockLow; insert after it
# Pattern: "  }" followed by newline then "  function escapeHtml"
anchor = "  }\n\n  function escapeHtml"
if anchor not in content:
    print(f"ERROR: anchor not found")
    exit(1)

content = content.replace(anchor, "  }\n" + shared_fn + "\n  function escapeHtml")
print("Step1: inserted _toTimeStr")

# ── Step 2: Remove toTimeStr from buildPlan (replace 6-line arrow function with blank) ──
# Pattern from HEAD shows exact whitespace:
#     const toTimeStr = (offsetMins) => {
#       const absMins = (arrivalMins + offsetMins) % (24 * 60);
#       const h = Math.floor(absMins / 60);
#       const m = absMins % 60;
#       return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
#     };
# followed by blank lines before "const isLow"
# We match from "    const toTimeStr" to the }; on its own line

bp_tts_pat = re.compile(
    r'\n    const toTimeStr = \(offsetMins\) => \{\n'
    r'      const absMins = \(arrivalMins \+ offsetMins\) % \(24 \* 60\);\n'
    r'      const h = Math\.floor\(absMins / 60\);\n'
    r'      const m = absMins % 60;\n'
    r"      return `\$\{String\(h\)\.padStart\(2,'0'\)\}:\$\{String\(m\)\.padStart\(2,'0'\)\}`;\n"
    r'    \};',
    re.DOTALL
)
before = len(content)
content = bp_tts_pat.sub('\n', content, count=1)
if len(content) < before:
    print("Step2: removed buildPlan toTimeStr")
else:
    print("Step2 WARNING: no match in buildPlan")

# ── Step 3: Remove toTimeStr from buildLowPowerPlan ──
# Same pattern, but in buildLowPowerPlan context
lp_tts_pat = re.compile(
    r'\n    const toTimeStr = \(offsetMins\) => \{\n'
    r'      const absMins = \(arrivalMins \+ offsetMins\) % \(24 \* 60\);\n'
    r'      const h = Math\.floor\(absMins / 60\);\n'
    r'      const m = absMins % 60;\n'
    r"      return `\$\{String\(h\)\.padStart\(2,'0'\)\}:\$\{String\(m\)\.padStart\(2,'0'\)\}`;\n"
    r'    \};',
    re.DOTALL
)
before = len(content)
content = lp_tts_pat.sub('\n', content, count=1)
if len(content) < before:
    print("Step3: removed buildLowPowerPlan toTimeStr")
else:
    print("Step3 WARNING: no match in buildLowPowerPlan")

# ── Step 4: Replace all remaining toTimeStr(...) calls with _toTimeStr(arrivalMins, ...) ──
content = content.replace('toTimeStr(', '_toTimeStr(arrivalMins, ')
print("Step4: replaced toTimeStr calls")

# ── Verify ──
remaining_defs = [l for l in content.split('\n') if 'const toTimeStr' in l]
if remaining_defs:
    print(f"WARNING: remaining local toTimeStr defs: {remaining_defs}")
else:
    print("Verify OK: no local toTimeStr definitions")

calls = [l for l in content.split('\n') if '_toTimeStr(arrivalMins,' in l]
print(f"  _toTimeStr call sites: {len(calls)}")

new_len = len(content)
print(f"Size: {orig_len} → {new_len} ({orig_len - new_len} bytes removed)")
print(f"Total lines: {content.count(chr(10)) + 1}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)