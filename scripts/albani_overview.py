import re, sys, collections
txt = open('/home/claude/work/txt/riyad_albani.txt', encoding='utf-8').read()
blocks = re.split(r'(?m)^=====PAGE (\S+) \| seq (\d+)=====$', txt)
# blocks: ['', page, seq, body, page, seq, body...]
entries = []
for i in range(1, len(blocks), 3):
    page, seq, body = blocks[i], blocks[i+1], blocks[i+2]
    entries.append((page, int(seq), body.strip()))
print("total blocks:", len(entries))
labels = collections.Counter()
for page, seq, body in entries:
    first = body.split('\n')[0]
    m = re.match(r'^(\d+)\s*-\s*\(([^)]*)\)', first)
    if m:
        labels[m.group(2)] += 1
    print(f"seq{seq:3d} p{page:>4} | {first[:100]}")
print(labels)
