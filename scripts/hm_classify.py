#!/usr/bin/env python3
"""Classify every hadith of each corpus against each of the other two. Saves classif.pkl
res[(X,Y)][x_id] = (tier, y_id, metrics, extra)"""
import collections, pickle, sys
sys.path.insert(0, "/home/claude/scripts")
from hm_tiers import classify, BM, compat, score  # noqa
D = "/home/claude/work/data/"
c = pickle.load(open(D + "corpora.pkl", "rb"))
for k in c:
    if k in ("riyad", "mishkat", "maalim"):
        for d in c[k]:
            d.setdefault("anchors", set())
by = {k: {d["id"]: d for d in c[k]} for k in ("riyad", "mishkat", "maalim")}


def pairs(X, Y):
    return pickle.load(open(D + f"pairs_{X}_{Y}.pkl", "rb"))


def unified(X, Y):
    out = collections.defaultdict(dict)
    for (x, y), m in pairs(X, Y).items():
        out[x][y] = m
    for (y, x), m in pairs(Y, X).items():
        if y in out[x]:
            continue
        out[x][y] = {"cAB": m["cBA"], "cBA": m["cAB"], "wAB": m["wBA"], "wBA": m["wAB"], "nA": m["nB"], "nB": m["nA"], "bAB": m["bBA"], "bBA": m["bAB"]}
    return out


res = {}
for X, Y in (("riyad", "mishkat"), ("riyad", "maalim"), ("maalim", "riyad"), ("maalim", "mishkat"), ("mishkat", "riyad"), ("mishkat", "maalim")):
    U = unified(X, Y)
    use_anchor = {X, Y} == {"riyad", "maalim"}
    r = {}
    for d in c[X]:
        r[d["id"]] = classify(d, U.get(d["id"], {}), by[Y], use_anchor=use_anchor)
    res[(X, Y)] = r
    print(X, "->", Y, dict(collections.Counter(v[0] for v in r.values())))
pickle.dump(res, open(D + "classif.pkl", "wb"))
pickle.dump(c, open(D + "corpora.pkl", "wb"))
