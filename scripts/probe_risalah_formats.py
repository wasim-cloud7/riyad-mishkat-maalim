import re, collections
T='/home/claude/work/txt/'
lines = open(T+'riyad_risalah.txt',encoding='utf-8').read().split('\n')
std = re.compile(r'^\s*(\d+)\s*/\s*(\d+)\s*[-–ـ]')
cands=[]
for i,l in enumerate(lines):
    s=l.strip()
    if not s or s.startswith('====='): continue
    if std.match(s): continue
    # any line beginning with a digit
    if re.match(r'^[0-9٠-٩]+', s):
        # skip chapter headings "36-باب"
        cands.append((i,s[:110]))
print(len(cands))
for i,s in cands[:140]:
    print(i, s)
