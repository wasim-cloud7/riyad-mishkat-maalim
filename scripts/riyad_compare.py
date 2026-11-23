#!/usr/bin/env python3
"""Word-level comparison of every aligned hadith between Fahl (A) and Risalah (B).

Every difference is classified:
  orth_convention   systematic spelling convention (الرحمان/الرحمن, مئة/مائة, ابن/بن, ...)
  connector         a one-letter prefix (و / ف / ب / ل) present in one edition only
  minor_word_form   one-letter or near-identical word form (typo-level or inflection)
  different_wording a different word / phrase
  extra_in_fahl     words present only in Fahl
  extra_in_risalah  words present only in Risalah

Outputs /home/claude/work/data/compare.json and compare_summary.json
Run: python3 -I riyad_compare.py
"""
import collections
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnorm import norm_loose, norm_orth, strip_diacritics  # noqa: E402

D = "/home/claude/work/data/"
f = json.load(open(D + "riyad_fahl.json", encoding="utf-8"))
r = json.load(open(D + "riyad_risalah.json", encoding="utf-8"))
al = json.load(open(D + "alignment.json", encoding="utf-8"))
fnum = {h["num"]: h for h in f["hadiths"]}
rseq = {h["num"]: h for h in r["hadiths"]}

FOOT = re.compile(r"\(\d{1,3}\)")
PAGE_MARK = re.compile(r"⦗[^⦘]*⦘")
QREF = re.compile(r"\[\s*[ء-يً-ٟ\s]{2,30}[:：]\s*[0-9٠-٩][0-9٠-٩\s،,\-–]*\]")
TAKHRIJ = {"رواه", "رواها", "رواهما", "رواهم", "متفق", "اخرجه", "ورواه", "رويناه", "رويناها", "وروياه"}
OPEN_Q = set("«“")
CLOSE_Q = set("»”")
HONORIFIC = {"واله", "اله", "وعلي", "وصحبه"}
_F = (r"(?:صلي الله عليه(?: واله)?(?: وصحبه)? وسلم|رضي الله (?:عنه|عنها|عنهما|عنهم|عنهن)|"
      r"عليه السلام|عليهما السلام|عليهم السلام|عز وجل|تبارك وتعالي|سبحانه وتعالي|سبحانه|تعالي|رحمه الله|رحمهم الله|رحمهما الله)")
FORMULA_SPAN = re.compile(r"^" + _F + r"(?: " + _F + r")*$")


# ------------------------------------------------------------------ equivalence helpers
def canon(tok):
    """Canonical form used only to test whether two tokens are orthographic variants."""
    t = tok
    t = re.sub(r"ماي(?=[هتوي]|$)", "مي", t)  # مائة/مئة and compounds (tier-B forms: مايه / ميه)
    t = t.replace("ماي", "مي")
    t = t.replace("الرحمان", "الرحمن").replace("السماوات", "السموات")
    t = t.replace("ههنا", "هاهنا")
    t = re.sub(r"داوود", "داود", t)
    if t.endswith("وا") and len(t) > 3:
        t = t[:-1]  # بنوا -> بنو, أولوا -> أولو
    if len(t) > 2 and t[-1] in "اي" and not t.endswith("وا"):
        t = t[:-1] + "ي"  # final alif / ya (الزنا/الزنى, منجا/منجي)
    return t


# curated equivalences after tier-B normalisation (hamza seats on waw / ya, doubled glides)
CURATED = [
    ("مسوول", "مسيول"), ("ومسوول", "ومسيول"), ("ومسوولهه", "ومسيولهه"), ("مسوولون", "مسيولون"),
    ("ومسوولة", "ومسيولة"), ("ومسووله", "ومسيوله"), ("مسوولة", "مسيولة"), ("مسوول", "مسيول"),
    ("جاووا", "جاوا"), ("فجاووا", "فجاوا"), ("اقرووا", "اقروا"), ("فابدووا", "فابداوا"), ("لابدووا", "لابداوا"),
    ("ابن", "بن"), ("يجي", "يجيي"), ("فيجي", "فيجيي"), ("شي", "شيي"), ("ملاها", "مليها"), ("ثلاثميه", "ثلاثمايه"),
    ("ثلاثه", "ثلاثة"), ("الحسين", "الحسيني"), ("اغنيتك", "اغنيك"),
]
CURATED_SET = {frozenset(p) for p in CURATED}
PREFIX = "وفبل"


def is_orth(a, b):
    if a == b:
        return True
    if frozenset((a, b)) in CURATED_SET:
        return True
    if canon(a) == canon(b):
        return True
    return False


def is_connector(a, b):
    if len(a) < len(b):
        a, b = b, a
    return len(a) == len(b) + 1 and a[0] in PREFIX and a[1:] == b and len(b) >= 2


def lev1(a, b):
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) <= 1
    if len(a) > len(b):
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def classify_replace(wa, wb):
    ca, cb = "".join(wa), "".join(wb)
    if len(wa) == 1 and len(wb) == 1:
        a, b = wa[0], wb[0]
        if is_orth(a, b):
            return "orth_convention"
        if is_connector(a, b):
            return "connector"
        if lev1(a, b) or (len(ca) >= 5 and difflib.SequenceMatcher(None, ca, cb).ratio() >= 0.86):
            return "minor_word_form"
        return "different_wording"
    if len(wa) <= 2 and len(wb) <= 2 and len(ca) >= 4 and difflib.SequenceMatcher(None, ca, cb).ratio() >= 0.86:
        return "minor_word_form"
    # multi-token: connector prefix on the first word only
    if len(wa) == len(wb) and all(is_orth(x, y) for x, y in zip(wa, wb)):
        return "orth_convention"
    return "different_wording"


# ------------------------------------------------------------------ tokenisation
def tokenise(raw, fahl):
    raw = PAGE_MARK.sub(" ", raw)
    raw = QREF.sub(" ", raw)
    if fahl:
        raw = FOOT.sub(" ", raw)
    depth = 0
    ascii_open = False
    toks = []
    for rt in raw.split():
        zone_here = "Q" if (depth > 0 or ascii_open) else "O"
        had_open = False
        for ch in rt:
            if ch in OPEN_Q:
                depth += 1
                had_open = True
            elif ch in CLOSE_Q:
                depth = max(0, depth - 1)
            elif ch == '"':
                if ascii_open:
                    ascii_open = False
                else:
                    ascii_open = True
                    had_open = True
        toks.append({"raw": rt, "zone": "Q" if (zone_here == "Q" or had_open) else "O"})
    return toks, (depth == 0 and not ascii_open)


def build(raw, fahl):
    toks, balanced = tokenise(raw, fahl)
    A, B, raws, zones, hz = [], [], [], [], []
    first_tak = None
    for k, t in enumerate(toks):
        A.extend(norm_orth(t["raw"]).split())
        for nt in norm_loose(t["raw"]).split():
            if first_tak is None and nt in TAKHRIJ:
                first_tak = len(B)
            B.append(nt)
            raws.append(k)
            zones.append(t["zone"])
    hz = ["H" if (first_tak is None or i < first_tak) else "T" for i in range(len(B))]
    return {"toks": toks, "A": A, "B": B, "rawidx": raws, "zone": zones, "hz": hz, "balanced": balanced}


def snippet(toks, i1, i2, ctx=4):
    j = lambda xs: " ".join(strip_diacritics(t["raw"]) for t in xs)  # noqa: E731
    return j(toks[max(0, i1 - ctx):i1]), j(toks[i1:i2]), j(toks[i2:i2 + ctx])


# ------------------------------------------------------------------ main loop
results = []
for p in al["pairs"]:
    fh, rh = fnum[p["fahl_num"]], rseq[p["risalah_seq"]]
    a, b = build(fh["raw"], True), build(rh["raw"], False)
    rec = {
        "fahl_num": fh["num"], "fahl_chapter": fh["chapter"],
        "risalah_printed": rh["printed_global"], "risalah_seq": rh["num"], "risalah_chapter": rh["chapter"],
        "sim": p["sim"], "moved_chapter": bool(p.get("moved_chapter")),
        "len_fahl": len(a["B"]), "len_risalah": len(b["B"]),
        "diffs": [], "n_spacing_ops": 0,
    }
    if a["A"] == b["A"]:
        status = "IDENTICAL"
    elif a["B"] == b["B"]:
        status = "HAMZA_ALIF_SPELLING_ONLY"
    else:
        sm = difflib.SequenceMatcher(None, a["B"], b["B"], autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            wa, wb = a["B"][i1:i2], b["B"][j1:j2]
            if tag == "replace" and "".join(wa) == "".join(wb):
                rec["n_spacing_ops"] += 1
                continue
            if tag == "replace":
                kind = classify_replace(wa, wb)
            elif tag == "delete":
                kind = "extra_in_fahl"
            else:
                kind = "extra_in_risalah"
            if (tag != "replace") and (set(wa + wb) <= HONORIFIC or FORMULA_SPAN.match(" ".join(wa + wb))):
                kind = "blessing_formula"
            zs = set(a["zone"][i1:i2]) | set(b["zone"][j1:j2])
            bal = a["balanced"] and b["balanced"]
            zone = "?" if not bal else ("Q" if "Q" in zs else "O")
            hzs = set(a["hz"][i1:i2]) | set(b["hz"][j1:j2])
            if not hzs:
                ref = a["hz"] if a["hz"] else ["H"]
                hzs = {ref[min(i1, len(ref) - 1)]}
            hzone = "H" if "H" in hzs else "T"
            ra = a["rawidx"][i1:i2] if i2 > i1 else ([a["rawidx"][min(i1, len(a["rawidx"]) - 1)]] if a["rawidx"] else [0])
            rb = b["rawidx"][j1:j2] if j2 > j1 else ([b["rawidx"][min(j1, len(b["rawidx"]) - 1)]] if b["rawidx"] else [0])
            ai1, ai2 = ra[0], (ra[-1] + 1 if i2 > i1 else ra[0])
            bi1, bi2 = rb[0], (rb[-1] + 1 if j2 > j1 else rb[0])
            la, ma, rra = snippet(a["toks"], ai1, ai2)
            lb, mb, rrb = snippet(b["toks"], bi1, bi2)
            rec["diffs"].append({
                "kind": kind, "zone": zone, "hzone": hzone,
                "n_fahl": len(wa), "n_risalah": len(wb),
                "fahl": ma, "risalah": mb,
                "ctx_fahl": f"{la} [[{ma}]] {rra}", "ctx_risalah": f"{lb} [[{mb}]] {rrb}",
            })
        kinds = {d["kind"] for d in rec["diffs"]}
        if not rec["diffs"]:
            status = "SPACING_ONLY"
        elif kinds <= {"orth_convention"}:
            status = "ORTHOGRAPHIC_CONVENTIONS_ONLY"
        elif kinds <= {"orth_convention", "connector"}:
            status = "CONNECTOR_LETTERS_ONLY"
        elif kinds <= {"orth_convention", "connector", "blessing_formula"}:
            status = "BLESSING_FORMULAE_ONLY"
        else:
            status = "WORDING_DIFFERENCES"
    rec["status"] = status
    sub = [d for d in rec["diffs"] if d["kind"] in ("extra_in_fahl", "extra_in_risalah", "different_wording", "minor_word_form")]
    rec["n_substantive"] = len(sub)
    rec["substantive_in_body"] = sum(1 for d in sub if d["hzone"] == "H")
    rec["tokens_added_fahl"] = sum(d["n_fahl"] for d in rec["diffs"] if d["kind"] == "extra_in_fahl")
    rec["tokens_added_risalah"] = sum(d["n_risalah"] for d in rec["diffs"] if d["kind"] == "extra_in_risalah")
    results.append(rec)

json.dump(results, open(D + "compare.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sc = collections.Counter(x["status"] for x in results)
kinds = collections.Counter(d["kind"] for x in results for d in x["diffs"])
summary = {
    "pairs": len(results),
    "status": dict(sc),
    "diff_kinds": dict(kinds),
    "wording_hadith": sc["WORDING_DIFFERENCES"],
    "wording_hadith_with_body_diff": sum(1 for x in results if x["status"] == "WORDING_DIFFERENCES" and x["substantive_in_body"] > 0),
    "wording_hadith_tail_only": sum(1 for x in results if x["status"] == "WORDING_DIFFERENCES" and x["substantive_in_body"] == 0),
}
json.dump(summary, open(D + "compare_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
