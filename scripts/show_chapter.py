import json, sys
sys.path.insert(0,'/home/claude/scripts')
from arnorm import norm_loose
D='/home/claude/work/data/'
f=json.load(open(D+'riyad_fahl.json')); r=json.load(open(D+'riyad_risalah.json'))
def show(ch, fch=None):
    fch = fch or ch
    fh=[h for h in f['hadiths'] if h['chapter']==fch]
    rh=[h for h in r['hadiths'] if h['chapter']==ch]
    print(f'=== chapter {ch}: Fahl {len(fh)} / Risalah {len(rh)}')
    n=max(len(fh),len(rh))
    for i in range(n):
        a = fh[i] if i<len(fh) else None
        b = rh[i] if i<len(rh) else None
        sa = f"F#{a['num']}: "+norm_loose(a['raw'])[:70] if a else '-'
        sb = f"R#{b['num']}(p{b['printed_global']}/{b['printed_local']}): "+norm_loose(b['raw'])[:70] if b else '-'
        print(sa); print('   ',sb)
for c in sys.argv[1:]:
    if ':' in c:
        a,b=c.split(':'); show(int(a),int(b))
    else: show(int(c))
