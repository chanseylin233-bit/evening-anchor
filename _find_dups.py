with open('E:/projects/evening-anchor/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('E:/projects/evening-anchor/_dups_found.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        if '洗个热水澡' in line or '泡脚 + 拉伸' in line:
            out.write(f"{i+1}: {line.rstrip()}\n")
    out.write("\nDone - total lines: " + str(len(lines)))