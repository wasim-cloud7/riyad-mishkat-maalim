import re, collections
T='/home/claude/work/txt/'
# ---------- Risalah ----------
lines = open(T+'riyad_risalah.txt',encoding='utf-8').read().split('\n')
pat = re.compile(r'^\s*(\d+)\s*/\s*(\d+)\s*[-–ـ]?')
hits=[]
for i,l in enumerate(lines):
    m = pat.match(l)
    if m: hits.append((i,int(m.group(1)),int(m.group(2)),l[:60]))
print('Risalah header-like lines:', len(hits))
glob=[h[2] for h in hits]
print('first', glob[:5], 'last', glob[-5:], 'max', max(glob))
# gaps / dups
c = collections.Counter(glob)
dups=[k for k,v in c.items() if v>1]
missing=[n for n in range(1,max(glob)+1) if n not in c]
print('dups',dups[:50], len(dups)); print('missing',missing[:80], len(missing))
# out of order
oo=[(glob[i-1],glob[i]) for i in range(1,len(glob)) if glob[i]!=glob[i-1]+1]
print('non-consecutive transitions:', oo[:60], len(oo))
print('FOOTNOTES blocks in risalah:', sum(1 for l in lines if l.startswith('-----FOOTNOTES')))
# ---------- Fahl ----------
lines2 = open(T+'riyad_fahl.txt',encoding='utf-8').read().split('\n')
pat2 = re.compile(r'^\s*(\d+)\s*[-–ـ]\s*(.*)$')
hits2=[]; chap2=[]
for i,l in enumerate(lines2):
    m = pat2.match(l)
    if m:
        rest=m.group(2)
        if rest.startswith('باب') or rest.startswith('بَاب') or rest.startswith('بَابُ'):
            chap2.append((i,int(m.group(1)),rest[:50]))
        else:
            hits2.append((i,int(m.group(1)),rest[:40]))
print('Fahl hadith-like:',len(hits2),'chapters-like:',len(chap2))
g2=[h[1] for h in hits2]
print('first',g2[:5],'last',g2[-5:],'max',max(g2))
c2=collections.Counter(g2)
print('dups', [k for k,v in c2.items() if v>1][:50], 'missing', [n for n in range(1,max(g2)+1) if n not in c2][:80])
oo2=[(g2[i-1],g2[i]) for i in range(1,len(g2)) if g2[i]!=g2[i-1]+1]
print('non-consecutive transitions:', oo2[:60], len(oo2))
print('chapters first/last:', chap2[:2], chap2[-2:])
print('FOOTNOTES blocks in fahl:', sum(1 for l in lines2 if l.startswith('-----FOOTNOTES')))
