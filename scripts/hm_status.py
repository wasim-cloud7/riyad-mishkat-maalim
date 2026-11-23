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


def _base_status(X, Y, xid):
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


RULE = {}  # (X, Y, xid) -> name of the rule that produced the final status


def _rescue(X, Y, xid):
    """Second pass for narrations the first pass could not place: the same hadith often appears in another narration
    (different wording / abridged / longer), which lowers the ordered-text score although the vocabulary overlap stays high.
    R1_bag      IN_PROBABLE : same or unknown narrator, both texts share >=28% of their rare-word mass, >=20 matched mass
    R4_contained IN_PROBABLE : same or unknown narrator, one text is >=75% contained in the other (abridgement)
    R2_weak     UNCERTAIN   : same or unknown narrator, 0.30<=S<0.45, >=15 matched mass, >=35% of one text found in the other
    R3_other    DIFF_COMPANION : other narrator, (S>=0.50 and >=20 matched mass) or (S>=0.45 and >=35), >=40% of one text found in the other
    returns (status, yid, metrics, S, rule) or None"""
    A = BY[X][xid]
    best = None
    for yid, mm in pairs(X, Y).get(xid, {}).items():
        B = BY[Y][yid]
        cp = compat(A, B)
        s = score(mm)
        w = max(mm["wAB"], mm["wBA"])
        bab, bba = mm.get("bAB", 0), mm.get("bBA", 0)
        bmax, bmin = max(bab, bba), min(bab, bba)
        cand = None
        if cp is not False and s >= 0.30 and bmin >= 0.28 and w >= 20:
            cand = ("IN_PROBABLE", 5, "R1_bag")
        elif cp is not False and bmax >= 0.75 and w >= 15 and s >= 0.25:
            cand = ("IN_PROBABLE", 4, "R4_contained")
        elif cp is not False and 0.30 <= s < 0.45 and w >= 15 and bmax >= 0.35:
            cand = ("UNCERTAIN", 3, "R2_weak")
        elif cp is False and ((s >= 0.50 and w >= 20) or (s >= 0.45 and w >= 35)) and bmax >= 0.40:
            cand = ("DIFF_COMPANION", 2, "R3_other")
        if cand and (best is None or (cand[1], s) > (best[0], best[1])):
            best = (cand[1], s, cand[0], yid, mm, cand[2])
    if best is None:
        return None
    return (best[2], best[3], best[4], round(best[1], 3), best[5])


def status_of(X, Y, xid):
    base = _base_status(X, Y, xid)
    RULE[(X, Y, xid)] = "base"
    if base[0] in ("IN_CONFIRMED", "IN_PROBABLE"):
        return base
    r = _rescue(X, Y, xid)
    if r is None:
        return base
    st, yid, mm, s, rule = r
    if base[0] == "NOT_IN" or (st == "IN_PROBABLE" and base[0] in ("UNCERTAIN", "DIFF_COMPANION")):
        RULE[(X, Y, xid)] = rule
        return st, yid, mm, s
    return base


_RANK = {"IN_CONFIRMED": 5, "IN_PROBABLE": 4, "UNCERTAIN": 3, "DIFF_COMPANION": 2, "NOT_IN": 1}


def _repeat_groups(X):
    """narrations repeated inside corpus X (S>=0.75, narrator not contradicting): they must share one status"""
    import os
    path = D + f"pairs_{X}_{X}.pkl"
    grp = {}
    if not os.path.exists(path):
        return grp
    for (x, y), m in pickle.load(open(path, "rb")).items():
        if x != y and score(m) >= 0.75 and compat(BY[X][x], BY[X][y]) is not False:
            grp.setdefault(x, set()).add(y)
            grp.setdefault(y, set()).add(x)
    return grp


def all_status(X, Y):
    st = {d["id"]: status_of(X, Y, d["id"]) for d in _c[X]}
    grp = _repeat_groups(X)
    out = dict(st)
    for x, partners in grp.items():
        best = max(partners, key=lambda y: _RANK[st[y][0]])
        if _RANK[st[best][0]] > _RANK[st[x][0]]:
            out[x] = st[best]
            RULE[(X, Y, x)] = f"repeat_of_{best}"
    return out


if __name__ == "__main__":
    import collections
    for X, Y in (("riyad", "mishkat"), ("riyad", "maalim"), ("maalim", "riyad"), ("maalim", "mishkat"), ("mishkat", "riyad"), ("mishkat", "maalim")):
        st = all_status(X, Y)
        print(X, "->", Y, dict(collections.Counter(v[0] for v in st.values())))
