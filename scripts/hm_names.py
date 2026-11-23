#!/usr/bin/env python3
"""Add narrator (companion) name sets to every doc in corpora.pkl, with carry-forward for 'وعنه' entries.
names1 = names before the first verb of speech (the narrator proper); names2 = every name-like token before the Prophet is mentioned."""
import pickle, collections
D = "/home/claude/work/data/"
c = pickle.load(open(D + "corpora.pkl", "rb"))
STOP = set("""عن وعن عنه وعنه عنها وعنها عنهما وعنهما عنهم وعنهم قال قالت قلت قيل سمعت سمع يقول تقول حدث حدثنا اخبرني ان انه انها
كان كانت سال سالت عند في من علي الي ثم اذ ابي ابو ابا ابن بن ام امي بنت اخي عبد الله مولي حديث رواية ايضا ذات يوم مع
كنا كنت اتي جاء جاءت دخل دخلت خرج رايت اني لما اذا لا ما هل يا بعض احد رجل امراة بينا نحن بينما نحن ثلاث بعث قدم""".split())
CUT = {"رسول", "نبي"}
VERB = {"قال", "قالت", "قلت", "ان", "انه", "انها", "سمعت", "سمع", "يقول", "تقول", "كان", "كانت", "حدث", "حدثنا", "كنا", "كنت", "بينا", "بينما", "اتي", "جاء", "رايت"}


ORD = set("""اول ثاني ثالث رابع خامس سادس سابع ثامن تاسع عاشر حادي عشر عشرون ثلاثون والعشرون اما احاديث الاحاديث فالاول فاول
والثاني والثالث والرابع والخامس والسادس والسابع والثامن والتاسع والعاشر حديث""".split())
START = {"عن", "وعن"}
ANAPH = {"عنه", "وعنه", "عنها", "وعنها", "عنهما", "وعنهما", "عنهم", "وعنهم"}


def skip_ordinal(toks):
    """Riyad entries may open with 'الثامن:' / 'وأما الأحاديث فالأول:' -> drop such leading tokens"""
    i = 0
    while i < len(toks) and toks[i] in ORD:
        i += 1
    return toks[i:]


def names_of(doc):
    """returns (names1, names2, kind) kind in {'name','anaph','none'}
    'name'  : entry opens with عن/وعن + narrator names
    'anaph' : entry opens with عنه/وعنها (the narrator of the previous entry)
    'none'  : continuation / variant / note lines (وفي رواية, رواه, ...): narrator unknown -> never compared"""
    toks = skip_ordinal(doc["full"][:34])
    if not toks:
        return set(), set(), "none"
    if toks[0] in ANAPH:
        return set(), set(), "anaph"
    if toks[0] not in START:
        return set(), set(), "none"
    chain = []
    for t in toks[1:]:
        if t in CUT:
            break
        chain.append(t)
    ok = lambda t: t not in STOP and (len(t) > 2 or t == "ذر")
    all_names = {t for t in chain if ok(t)}
    prim = []
    for t in chain:
        if t in VERB and prim:
            break
        prim.append(t)
    prim_names = {t for t in prim if ok(t)}
    if chain and chain[0] == "علي":  # 'علي' is also the preposition 'على' -> accepted only as the first word after عن
        all_names.add("علي")
        prim_names.add("علي")
    return prim_names, all_names, "name"


for key in ("riyad", "mishkat", "maalim"):
    prev1, prev2 = set(), set()
    unknown = 0
    kinds = collections.Counter()
    for d in c[key]:
        n1, n2, kind = names_of(d)
        d.pop("names_carried", None)
        if kind == "anaph":
            n1, n2 = set(prev1), set(prev2)
            d["names_carried"] = True
        kinds[kind] += 1
        d["names1"], d["names2"] = frozenset(n1), frozenset(n2)
        if kind == "name" and n1:
            prev1, prev2 = n1, n2
        if not n1:
            unknown += 1
    print(key, "docs without a narrator name:", unknown, "of", len(c[key]), dict(kinds))
pickle.dump(c, open(D + "corpora.pkl", "wb"))
for key, i in (("riyad", 1691), ("mishkat", 2), ("maalim", 4), ("maalim", 1566)):
    d = [x for x in c[key] if x["id"] == i][0]
    print(key, i, sorted(d["names1"])[:6], sorted(d["names2"])[:8])
