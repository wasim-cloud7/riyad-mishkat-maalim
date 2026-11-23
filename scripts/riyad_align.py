#!/usr/bin/env python3
"""Align hadith blocks of the Risalah and Fahl editions chapter by chapter (DP on text similarity)
and save alignment.json.

Run: python3 -I riyad_align.py
"""
import collections
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnorm import norm_formula  # noqa: E402

D = "/home/claude/work/data/"
f = json.load(open(D + "riyad_fahl.json", encoding="utf-8"))
r = json.load(open(D + "riyad_risalah.json", encoding="utf-8"))

FOOT_MARK = re.compile(r"\(\d{1,3}\)")


def prep(h, fahl):
    raw = h["raw"]
    if fahl:
        raw = FOOT_MARK.sub(" ", raw)
    toks = norm_formula(raw).split()
    return toks


for h in f["hadiths"]:
    h["toks"] = prep(h, True)
for h in r["hadiths"]:
    h["toks"] = prep(h, False)


def sim(a, b):
    """Similarity of two token lists in [0,1]; robust to a long tail of commentary on one side."""
    if not a or not b:
        return 0.0
    # compare leading windows (the narrator + start of the matn), then full text
    n = 40
    sa, sb = a[:n], b[:n]
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    head = sm.ratio()
    if head < 0.35:
        return head * 0.5
    full = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    return max(head * 0.6 + full * 0.4, full)


def align_chapter(A, B, thr=0.45):
    n, m = len(A), len(B)
    W = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            W[i][j] = sim(A[i]["toks"], B[j]["toks"])
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bt = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best = dp[i - 1][j]
            op = "U"  # skip A
            if dp[i][j - 1] > best:
                best, op = dp[i][j - 1], "L"
            w = W[i - 1][j - 1]
            if w >= thr and dp[i - 1][j - 1] + w > best:
                best, op = dp[i - 1][j - 1] + w, "D"
            dp[i][j] = best
            bt[i][j] = op
    i, j = n, m
    pairs, onlyA, onlyB = [], [], []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and bt[i][j] == "D":
            pairs.append((i - 1, j - 1, W[i - 1][j - 1]))
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or bt[i][j] == "U"):
            onlyA.append(i - 1)
            i -= 1
        else:
            onlyB.append(j - 1)
            j -= 1
    pairs.reverse()
    onlyA.reverse()
    onlyB.reverse()
    return pairs, onlyA, onlyB


fby = collections.defaultdict(list)
rby = collections.defaultdict(list)
for h in f["hadiths"]:
    fby[h["chapter"]].append(h)
for h in r["hadiths"]:
    rby[h["chapter"]].append(h)

result = {"pairs": [], "only_fahl": [], "only_risalah": [], "chapters": {}}
for c in range(1, 373):
    A, B = fby.get(c, []), rby.get(c, [])
    pairs, oa, ob = align_chapter(A, B)
    for i, j, w in pairs:
        result["pairs"].append(
            {
                "chapter": c,
                "fahl_num": A[i]["num"],
                "risalah_seq": B[j]["num"],
                "risalah_printed": B[j]["printed_global"],
                "risalah_local": B[j]["printed_local"],
                "sim": round(w, 4),
            }
        )
    for i in oa:
        result["only_fahl"].append({"chapter": c, "fahl_num": A[i]["num"], "start": " ".join(A[i]["toks"][:25])})
    for j in ob:
        result["only_risalah"].append(
            {
                "chapter": c,
                "risalah_seq": B[j]["num"],
                "risalah_printed": B[j]["printed_global"],
                "risalah_local": B[j]["printed_local"],
                "start": " ".join(B[j]["toks"][:25]),
            }
        )
    result["chapters"][c] = {"fahl": len(A), "risalah": len(B), "paired": len(pairs), "only_fahl": len(oa), "only_risalah": len(ob)}

# ---- cross-chapter post-pass: pair leftovers that landed in different chapters in the two editions
fnum = {h["num"]: h for h in f["hadiths"]}
rseq = {h["num"]: h for h in r["hadiths"]}
moved = []
for x in list(result["only_fahl"]):
    best, bj = 0.0, None
    for y in result["only_risalah"]:
        w = sim(fnum[x["fahl_num"]]["toks"], rseq[y["risalah_seq"]]["toks"])
        if w > best:
            best, bj = w, y
    if bj is not None and best >= 0.6:
        result["pairs"].append(
            {
                "chapter": x["chapter"],
                "chapter_risalah": bj["chapter"],
                "fahl_num": x["fahl_num"],
                "risalah_seq": bj["risalah_seq"],
                "risalah_printed": bj["risalah_printed"],
                "risalah_local": bj["risalah_local"],
                "sim": round(best, 4),
                "moved_chapter": True,
            }
        )
        result["only_fahl"].remove(x)
        result["only_risalah"].remove(bj)
        moved.append((x["fahl_num"], bj["risalah_seq"], x["chapter"], bj["chapter"]))
result["moved_chapter_pairs"] = moved
result["pairs"].sort(key=lambda p: p["fahl_num"])
json.dump(result, open(D + "alignment.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cross-chapter pairs:", moved)
print("pairs:", len(result["pairs"]), "only_fahl:", len(result["only_fahl"]), "only_risalah:", len(result["only_risalah"]))
lo = [p for p in result["pairs"] if p["sim"] < 0.8]
print("pairs with sim<0.8:", len(lo))
for p in lo[:40]:
    print("  low-sim:", p)
print("--- only in Fahl:")
for x in result["only_fahl"]:
    print("  ", x)
print("--- only in Risalah:")
for x in result["only_risalah"]:
    print("  ", x)
