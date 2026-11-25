"""Rare-word cross-check of the sahih Riyad hadith that were classed as clearly LEFT OUT of Mishkat / Ma'alim.
For each hadith: its 8 rarest words (idf) are looked up in every Mishkat entry / Ma'alim block; an entry sharing 5 or more of them is flagged for a human look.
It can only find hadith that share unusual words, so it lowers the chance of a missed counterpart but cannot prove there is none."""
import pickle, csv, sys, re, collections
sys.path.insert(0,'/home/claude/scripts')
c=pickle.load(open('/home/claude/work/data/corpora.pkl','rb'))
idf=c['idf']
R={d['id']:d for d in c['riyad']}
MI=c['mishkat']; MA=c['maalim']
print(c['riyad'][0].keys())
rows=list(csv.DictReader(open('/home/claude/outputs/phase2/phase2_master_riyad.csv',encoding='utf-8-sig')))
S=[r for r in rows if r['combined_class']=='SAHIH']
mis_out=[int(r['fahl_no']) for r in S if r['mishkat_3state']=='OUT']
mal_out=[int(r['fahl_no']) for r in S if r['maalim_3state']=='OUT']
print(len(mis_out),len(mal_out), 'sample id', c['riyad'][0]['id'], c['mishkat'][0]['id'], c['maalim'][0]['id'])
post={}
def build(docs,name):
    p=collections.defaultdict(set)
    for i,d in enumerate(docs):
        for t in set(d['full']): p[t].add(i)
    return p
pm=build(MI,'mis'); pl=build(MA,'mal')
def search(rid, docs, post, k=8, need=5):
    d=R[rid]
    toks=[t for t in set(d['body'] or d['full']) if t in idf and len(t)>2]
    toks.sort(key=lambda t:-idf[t])
    top=toks[:k]
    if len(top)<k: return top,[]
    cnt=collections.Counter()
    for t in top:
        for i in post.get(t,()): cnt[i]+=1
    hits=[(n,i) for i,n in cnt.items() if n>=need]
    hits.sort(reverse=True)
    return top,hits[:5]
out=[]
for name,ids,docs,post_ in (('mishkat',mis_out,MI,pm),('maalim',mal_out,MA,pl)):
    flagged=[]
    for f in ids:
        top,hits=search(f,docs,post_)
        if hits: flagged.append((f,top,hits))
    print(name,'flagged',len(flagged),'of',len(ids))
    out.append((name,flagged))
pickle.dump(out,open('/home/claude/work/data/crosscheck_flags.pkl','wb'))
