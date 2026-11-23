import json, collections
D='/home/claude/work/data/'
f=json.load(open(D+'riyad_fahl.json')); r=json.load(open(D+'riyad_risalah.json'))
fc=collections.Counter(h['chapter'] for h in f['hadiths'])
rc=collections.Counter(h['chapter'] for h in r['hadiths'])
print('Fahl chapters:',len(f['chapters']),' Risalah chapters:',len(r['chapters']))
print('Fahl missing chapter nums:', [n for n in range(1,373) if str(n) not in f['chapters']])
print('Risalah missing chapter nums:', [n for n in range(1,373) if str(n) not in r['chapters']])
diff=[(c,fc.get(c,0),rc.get(c,0)) for c in range(1,373) if fc.get(c,0)!=rc.get(c,0)]
print('chapters with different hadith counts (chapter, fahl, risalah):', diff)
print(sum(fc.values()), sum(rc.values()))
