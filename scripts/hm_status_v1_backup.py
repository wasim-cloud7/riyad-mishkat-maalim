#!/usr/bin/env python3
"""Final presence status of a hadith of corpus X inside corpus Y (built on classif.pkl + pairs_*.pkl).

Statuses (strongest first)
  IN_CONFIRMED   same hadith found (text match S>=0.75 / both-way coverage >=0.6, or Bukhari/Muslim number anchor agrees)
  IN_PROBABLE    probable same hadith in another narration/abridgement: POSSIBLE tier with S>=0.62, bag coverage>=0.5 and enough matched mass
  UNCERTAIN      weaker resemblance (POSSIBLE tier below the probable bar, or a near-miss 0.45<=S<0.55 with compatible Companion)
  DIFF_COMPANION nearly identical wording but a different Companion/narrator (a distinct hadith, shown separately)
  NOT_IN         nothing comparable found
The sets used for headline numbers: strict = IN_CONFIRMED ; inclusive = IN_CONFIRMED + IN_PROBABLE.
"""
import pickle
import sys

sys.path.insert(0, "/home/claude/scripts")
from hm_tiers import compat, score  # noqa: E402

D = "/home/claude/work/data/"
_c = pickle.load(open(D + "corpora.pkl", "rb"))
_cls = pickle.load(open(D + "classif.pkl", "rb"))
BY = {k: {d["id"]: d for d in _c[k]} for k in ("riyad", "mishkat", "maalim")}


def _unified(X, Y):
    out = {}
    for (x, y), m in pickle.load(open(D + f"pairs_{X}_{Y}.pkl", "rb")).items():
        out.setdefault(x, {})[y] = m
    for (y, x), m in pickle.load(open(D + f"pairs_{Y}_{X}.pkl", "rb")).items():
        if y not in out.get(x, {}):
            out.setdefault(x, {})[y] = {"cAB": m["cBA"], "cBA": m["cAB"], "wAB": m["wBA"], "wBA": m["wAB"], "nA": m["nB"], "nB": m["nA"], "bAB": m["bBA"], "bBA": m["bAB"]}
    return out


_PAIRS = {}


def pairs(X, Y):
    if (X, Y) not in _PAIRS:
        _PAIRS[(X, Y)] = _unified(X, Y)
    return _PAIRS[(X, Y)]


def status_of(X, Y, xid):
    tier, tid, m, ex = _cls[(X, Y)][xid]
    if tier in ("IN_TEXT", "IN_ANCHOR_TEXT", "IN_ANCHOR_ONLY"):
        return "IN_CONFIRMED", tid, m, ex["score"] if ex else None
    if tier == "POSSIBLE":
        s = ex["score"]
        mass_ok = max(m["wAB"], m["wBA"]) >= 10
        if mass_ok and s >= 0.62 and max(m.get("bAB", 0), m.get("bBA", 0)) >= 0.5:
            return "IN_PROBABLE", tid, m, s
        if mass_ok:
            return "UNCERTAIN", tid, m, s
        # stub / too little matched text: fall through to look for a better candidate
    if tier == "OTHER_COMPANION":
        return "DIFF_COMPANION", tid, m, ex["score"]
    # near-miss search among all candidates
    A = BY[X][xid]
    best = None
    for yid, mm in pairs(X, Y).get(xid, {}).items():
        B = BY[Y][yid]
        s = score(mm)
        cp = compat(A, B)
        if cp is False or max(mm["wAB"], mm["wBA"]) < 10:
            continue
        if 0.45 <= s < 0.62 and (best is None or s > best[0]):
            best = (s, yid, mm)
    if best:
        return "UNCERTAIN", best[1], best[2], round(best[0], 3)
    return "NOT_IN", None, None, None


def all_status(X, Y):
    return {d["id"]: status_of(X, Y, d["id"]) for d in _c[X]}


if __name__ == "__main__":
    import collections
    for X, Y in (("riyad", "mishkat"), ("riyad", "maalim"), ("maalim", "riyad"), ("maalim", "mishkat"), ("mishkat", "riyad"), ("mishkat", "maalim")):
        st = all_status(X, Y)
        print(X, "->", Y, dict(collections.Counter(v[0] for v in st.values())))
