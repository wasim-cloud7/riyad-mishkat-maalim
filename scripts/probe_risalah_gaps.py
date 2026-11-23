import re
T='/home/claude/work/txt/'
lines = open(T+'riyad_risalah.txt',encoding='utf-8').read().split('\n')
pat = re.compile(r'^\s*(\d+)\s*/\s*(\d+)')
idx={}
order=[]
for i,l in enumerate(lines):
    m=pat.match(l)
    if m:
        order.append((i,int(m.group(2))))
# show neighborhood for a handful of gaps
want=[(60,62),(134,139),(288,989),(340,241),(345,347),(415,417),(500,502),(514,516),(535,537),(700,702)]
pos={}
for k,(i,n) in enumerate(order):
    pos.setdefault(n,[]).append(i)
def show(a,b):
    ia=pos[a][0]; ib=pos[b][0]
    print(f'---- between header {a} (line {ia}) and header {b} (line {ib})')
    for j in range(ia, min(ib+1, ia+40)):
        print(j, lines[j][:150])
for a,b in want[:6]:
    show(a,b)
