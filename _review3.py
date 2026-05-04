import re

with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find toTimeStr definition and all usages
for i, line in enumerate(lines):
    if 'toTimeStr' in line:
        print(f"{i+1}: {line.rstrip()}")
    
print()
# Find buildPlan ends around line 1900
for i, line in enumerate(lines):
    if 1905 <= i+1 <= 1920:
        print(f"{i+1}: {line.rstrip()}")

print()
# Check toTimeStr in buildLowPowerPlan context
print("=== buildLowPowerPlan region (1935-1980) ===")
for i, line in enumerate(lines):
    if 1935 <= i+1 <= 1980:
        print(f"{i+1}: {line.rstrip()}")