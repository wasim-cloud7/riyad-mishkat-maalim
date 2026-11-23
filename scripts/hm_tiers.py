import pickle, collections
D = "/home/claude/work/data/"
BM = lambda s: {x for x in s if x[0] in ("B", "M")}


def compat(A, B):
    if not A["names1"] or not B["names1"]:
        return None
    return bool((A["names1"] & B["names2"]) or (B["names1"] & A["names2"]))


def score(m):
    return max(m["cAB"], m["cBA"]) + 0.3 * min(m["cAB"], m["cBA"])


def classify(src_doc, cands, tgt_by_id, use_anchor=True):
    """cands: dict tgt_id -> metrics. returns (tier, tgt_id, metrics, extra)"""
    best = None
    for tid, m in cands.items():
        B = tgt_by_id[tid]
        cp = compat(src_doc, B)
        anc = use_anchor and bool(BM(src_doc["anchors"]) & BM(B["anchors"]))
        s = score(m)
        strong = (s >= 0.75) or (m["cAB"] >= 0.6 and m["cBA"] >= 0.6)
        if anc and cp is not False:
            tier = "IN_ANCHOR_TEXT" if s >= 0.45 else "IN_ANCHOR_ONLY"
            rank = 5 if tier == "IN_ANCHOR_TEXT" else 4
        elif strong and cp is not False:
            tier, rank = "IN_TEXT", 3
        elif s >= 0.55 and cp is not False:
            tier, rank = "POSSIBLE", 2
        elif s >= 0.6 and cp is False:
            tier, rank = "OTHER_COMPANION", 1
        else:
            continue
        cand = (rank, s, tid, tier, m, cp, anc)
        if best is None or cand[:2] > best[:2]:
            best = cand
    if best is None:
        return ("NOT_IN", None, None, None)
    return (best[3], best[2], best[4], {"compat": best[5], "anchor": best[6], "score": round(best[1], 3)})
