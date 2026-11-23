#!/usr/bin/env python3
"""Candidate retrieval + verification between two hadith corpora.

usage: python3 -I hm_match.py SRC TGT        (SRC, TGT in riyad|mishkat|maalim)
Writes /home/claude/work/data/pairs_SRC_TGT.pkl : dict (src_id, tgt_id) -> metrics
metrics: cAB (share of SRC's main narration found, in order, in TGT), cBA (share of TGT's main narration found in SRC),
         wAB (idf mass matched), nA (idf mass of SRC body), nB (idf mass of TGT body)
"""
import collections
import difflib
import math
import pickle
import sys
import time

D = "/home/claude/work/data/"
c = pickle.load(open(D + "corpora.pkl", "rb"))
idf = c["idf"]
CAP_BODY, CAP_FULL = 260, 420


def mass(toks):
    return sum(idf[t] for t in toks)


class Index:
    def __init__(self, docs, maxdf_frac=0.12):
        self.docs = docs
        self.post = collections.defaultdict(list)
        self.setmass = []
        for i, d in enumerate(docs):
            st = set(d["full"])
            self.setmass.append(sum(idf[t] for t in st))
            for t in st:
                self.post[t].append(i)
        self.maxdf = max(30, maxdf_frac * len(docs))

    def query(self, toks, k_cos=6, k_cont=4):
        st = set(toks)
        sa = sum(idf[t] for t in st) + 1e-9
        acc = collections.defaultdict(float)
        for t in st:
            p = self.post.get(t)
            if not p or len(p) > self.maxdf:
                continue
            w = idf[t]
            for i in p:
                acc[i] += w
        if not acc:
            return []
        cos = sorted(((v / math.sqrt(sa * self.setmass[i] + 1e-9), i) for i, v in acc.items()), reverse=True)[:k_cos]
        cont = sorted(((v / sa, i) for i, v in acc.items()), reverse=True)[:k_cont]
        return list({i for _, i in cos} | {i for _, i in cont})


def cov(a, b):
    """idf-weighted share of token list a found, in order, inside token list b"""
    if not a or not b:
        return 0.0, 0.0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    w = 0.0
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w += idf[a[blk.a + k]]
    return w / (mass(a) + 1e-9), w


def bag(a, b):
    if not a or not b:
        return 0.0
    sb = set(b)
    return sum(idf[t] for t in a if t in sb) / (mass(a) + 1e-9)


def verify(A, B):
    a_body, b_full = A["body"][:CAP_BODY], B["full"][:CAP_FULL]
    b_body, a_full = B["body"][:CAP_BODY], A["full"][:CAP_FULL]
    cAB, wAB = cov(a_body, b_full)
    cBA, wBA = cov(b_body, a_full)
    return {"cAB": round(cAB, 4), "cBA": round(cBA, 4), "wAB": round(wAB, 2), "wBA": round(wBA, 2),
            "nA": round(mass(a_body), 2), "nB": round(mass(b_body), 2),
            "bAB": round(bag(a_body, b_full), 4), "bBA": round(bag(b_body, a_full), 4)}


def run(src, tgt):
    S, T = c[src], c[tgt]
    ix = Index(T)
    out = {}
    t0 = time.time()
    for n, A in enumerate(S):
        if not A["full"]:
            continue
        for j in ix.query(A["full"]):
            B = T[j]
            out[(A["id"], B["id"])] = verify(A, B)
        if n % 500 == 0:
            print(src, tgt, n, len(S), round(time.time() - t0, 1), "s", len(out), "pairs", flush=True)
    pickle.dump(out, open(D + f"pairs_{src}_{tgt}.pkl", "wb"))
    print("done", src, tgt, len(out), "pairs", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
