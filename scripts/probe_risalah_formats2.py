import re, collections
T='/home/claude/work/txt/'
lines = open(T+'riyad_risalah.txt',encoding='utf-8').read().split('\n')
std = re.compile(r'^\s*(\d+)\s*/\s*(\d+)\s*[-–ـ]')
chap = re.compile(r'^\s*\d+\s*[-–ـ]?\s*(با[بَ]|بَا?ب|بيان وجوب)')
out=[]
for i,l in enumerate(lines):
    s=l.strip()
    if not s or s.startswith('====='): continue
    if std.match(s): continue
    if re.match(r'^[0-9٠-٩]+', s) and not chap.match(s):
        out.append((i,s[:130]))
print(len(out))
for i,s in out: print(i,s)
