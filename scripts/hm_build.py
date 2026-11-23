#!/usr/bin/env python3
"""Build the three comparable corpora (Riyad = al-Fahl, Mishkat, Ma'alim) with cleaned token lists, anchors and
grade information, and save them to /home/claude/work/data/corpora.pkl

Each doc: id, text (for display), body (tokens of the main narration), full (all tokens), mass fields later.
Run: python3 -I hm_build.py
"""
import collections
import json
import math
import os
import pickle
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnorm import norm_formula, strip_diacritics  # noqa: E402

D = "/home/claude/work/data/"
FOOT = re.compile(r"\(\d{1,3}\)")
PAGE_MARK = re.compile(r"⦗[^⦘]*⦘")
QREF = re.compile(r"\[\s*[ء-يً-ٟ\s]{2,30}[:：]\s*[0-9٠-٩][0-9٠-٩\s،,\-–]*\]")
REFBR = re.compile(r"\[[^\[\]]*\d[^\[\]]*\]")
TAKHRIJ = {"رواه", "رواها", "رواهما", "رواهم", "متفق", "اخرجه", "ورواه", "رويناه", "رويناها", "وروياه", "وراه", "رواة"}
_F = (r"(?:صلي الله عليه(?: واله)?(?: وصحبه)? وسلم|صلي الله عليه وعلي اله وسلم|رضي الله (?:عنه|عنها|عنهما|عنهم|عنهن)|"
      r"عليه السلام|عليهما السلام|عليهم السلام|عز وجل|تبارك وتعالي|سبحانه وتعالي|سبحانه|تعالي|رحمه الله|رحمهم الله|رحمهما الله)")
FORMULA = re.compile(r"\b" + _F + r"\b")
ARDIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def norm_text(s):
    s = norm_formula(s)
    s = FORMULA.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def toks_of(s):
    return [t for t in norm_text(s).split() if len(t) > 1]


def split_body(tokens):
    """Cut at the first takhrij marker unless it opens the entry (variant entries start with 'ورواه ...')."""
    for i, t in enumerate(tokens):
        if t in TAKHRIJ:
            if i >= 5:
                return tokens[:i]
            return tokens
    return tokens


# ------------------------------------------------------------------ anchors
SRC_CODES = {"خ": "B", "م": "M", "د": "D", "ت": "T", "ن": "N", "س": "N", "جه": "J", "ق": "BM", "حم": "A", "ك": "H", "حب": "I"}


def parse_maalim_refs(refs):
    """['خ8، م16', 'ت2616/جه3973'] -> {('B',8),('M',16),('T',2616),('J',3973)}"""
    out = set()
    for r in refs:
        r = r.translate(ARDIG)
        for part in re.split(r"[،,/؛;]", r):
            part = part.strip()
            m = re.match(r"^(خ|م|د|ت|ن|س|جه|حم|ك|حب|هق|ط|عب|ش|حل|قط)\s*ـ*\s*([\d]+)", part)
            if m:
                code = SRC_CODES.get(m.group(1), m.group(1))
                out.add((code, int(m.group(2))))
    return out


def parse_fahl_anchors(footnotes):
    """Bukhari / Muslim (and other) numbers from al-Fahl's takhrij footnotes."""
    out = set()
    for fn in footnotes or []:
        fn = fn.translate(ARDIG)
        if "أخرجه" not in fn and "اخرجه" not in fn and "البخاري" not in fn and "مسلم" not in fn:
            continue
        for m in re.finditer(r"البخاري[^()]{0,40}?\((\d+)\)", fn):
            out.add(("B", int(m.group(1))))
        for m in re.finditer(r"مسلم[^()]{0,40}?\((\d+)\)", fn):
            out.add(("M", int(m.group(1))))
        for m in re.finditer(r"(?:أبو|ابو) داود[^()]{0,40}?\((\d+)\)", fn):
            out.add(("D", int(m.group(1))))
        for m in re.finditer(r"الترمذي[^()]{0,40}?\((\d+)\)", fn):
            out.add(("T", int(m.group(1))))
        for m in re.finditer(r"ابن ماجه[^()]{0,40}?\((\d+)\)", fn):
            out.add(("J", int(m.group(1))))
        for m in re.finditer(r"النسائي[^()]{0,40}?\((\d+)\)", fn):
            out.add(("N", int(m.group(1))))
    return out


# Nawawi's own attribution inside the Riyad text
EXCL = re.compile(r"(على شرط|بشرط|شرط)\s+(البخاري|مسلم|الشيخين|ومسلم|البخاري ومسلم|هما)")


def riyad_attribution(raw):
    s = norm_formula(PAGE_MARK.sub(" ", FOOT.sub(" ", raw)))
    s = EXCL.sub(" ", s)
    both = "متفق عليه" in s
    b = bool(re.search(r"(رواه|اخرجه|رواهما|ورواه|رويناه|وراه|رواية|روايه)[^.]{0,30}البخاري", s)) or "في صحيح البخاري" in s
    m = bool(re.search(r"(رواه|اخرجه|رواهما|ورواه|رويناه|وراه|رواية|روايه|لمسلم)[^.]{0,30}(مسلم)", s)) or "في صحيح مسلم" in s or "لمسلم" in s
    sh = bool(re.search(r"(رواه|رواهما|اخرجه)[^.]{0,20}الشيخان", s)) or "في الصحيحين" in s
    if both or sh or (b and m):
        return "BOTH"
    if b:
        return "BUKHARI"
    if m:
        return "MUSLIM"
    return "NONE"


def main():
    f = json.load(open(D + "riyad_fahl.json", encoding="utf-8"))
    alb = json.load(open(D + "albani.json", encoding="utf-8"))
    mis = json.load(open(D + "mishkat.json", encoding="utf-8"))
    mal = json.load(open(D + "maalim.json", encoding="utf-8"))

    alb_by_fahl = {}
    for a in alb:
        if a["kind"] == "hadith" and a.get("fahl_num"):
            alb_by_fahl[a["fahl_num"]] = a

    riyad = []
    for h in f["hadiths"]:
        raw = QREF.sub(" ", PAGE_MARK.sub(" ", FOOT.sub(" ", h["raw"])))
        toks = toks_of(raw)
        body = split_body(toks)
        a = alb_by_fahl.get(h["num"])
        riyad.append({
            "id": h["num"], "chapter": h["chapter"], "text": re.sub(r"\s+", " ", raw).strip(),
            "full": toks, "body": body,
            "attrib": riyad_attribution(h["raw"]),
            "anchors": parse_fahl_anchors(h.get("footnotes")),
            "albani_label": a["label"] if a else None, "albani_num": a["albani_num"] if a else None,
            "albani_footnote": a["footnote"] if a else None,
        })

    mishkat = []
    for e in mis:
        toks = toks_of(e["text"])
        mishkat.append({
            "id": e["num"], "text": re.sub(r"\s+", " ", e["text"]).strip(), "full": toks, "body": split_body(toks),
            "label": e["label"], "family": e["family"], "book": e["book"], "bab": e["bab"], "fasl": e["fasl"],
        })

    maalim = []
    for e in mal:
        if e["kind"] != "hadith":
            continue
        main_txt = REFBR.sub(" ", e["main"])
        full_txt = REFBR.sub(" ", e["text"].replace("□", " "))
        full_txt = FOOT.sub(" ", full_txt)
        main_txt = FOOT.sub(" ", main_txt)
        anchors = parse_maalim_refs(e["refs"])
        flags = e.get("flags") or ""
        if "ق" in flags:
            attrib = "BOTH"
        elif "خ" in flags:
            attrib = "BUKHARI"
        elif "م" in flags:
            attrib = "MUSLIM"
        else:
            attrib = "NONE"
        maalim.append({
            "id": e["seq"], "bookno": e["bookno"], "text": re.sub(r"\s+", " ", full_txt).strip(),
            "full": toks_of(full_txt), "body": toks_of(main_txt), "flags": flags, "attrib": attrib, "anchors": anchors,
            "grades": e["grades"], "notes": e["notes"], "refs": e["refs"], "chapter": e["chapter"],
        })

    # ---- light prefix normalisation using corpus vocabulary
    vocab = collections.Counter()
    for corp in (riyad, mishkat, maalim):
        for d in corp:
            vocab.update(d["full"])
    NOSTEM = {"الله", "الذي", "التي", "الذين", "الي", "الا", "الان", "اللهم", "الناس"}

    cache = {}

    def stem(t):
        if t in cache:
            return cache[t]
        s = t
        if len(s) > 3 and s[0] in "وف" and vocab.get(s[1:], 0) >= 15:
            s = s[1:]
        if len(s) >= 5 and s.startswith("ال") and s not in NOSTEM:
            s = s[2:]
        elif len(s) >= 5 and s[0] in "وفبكل" and s[1:3] == "ال" and vocab.get(s[1:], 0) >= 15:
            s = s[3:]
        cache[t] = s
        return s

    for corp in (riyad, mishkat, maalim):
        for d in corp:
            d["full"] = [stem(t) for t in d["full"]]
            d["body"] = [stem(t) for t in d["body"]]

    # ---- idf over all docs
    df = collections.Counter()
    ndocs = 0
    for corp in (riyad, mishkat, maalim):
        for d in corp:
            df.update(set(d["full"]))
            ndocs += 1
    idf = {t: math.log((ndocs + 1) / (c + 0.5)) for t, c in df.items()}
    pickle.dump({"riyad": riyad, "mishkat": mishkat, "maalim": maalim, "idf": idf, "ndocs": ndocs}, open(D + "corpora.pkl", "wb"))

    print("docs:", len(riyad), len(mishkat), len(maalim), "vocab:", len(df))
    r1 = riyad[0]
    print("F#1 body tokens:", len(r1["body"]), " ".join(r1["body"][:40]))
    print("F#1 attrib:", r1["attrib"], "anchors:", sorted(r1["anchors"]))
    m2 = [d for d in mishkat if d["id"] == 2][0]
    print("Mishkat#2:", m2["label"], m2["family"], len(m2["body"]), " ".join(m2["body"][:30]))
    a4 = [d for d in maalim if d["id"] == 4][0]
    print("Ma'alim#4:", a4["flags"], a4["attrib"], sorted(a4["anchors"]), " ".join(a4["body"][:30]))
    print("Riyad attribution counts:", collections.Counter(d["attrib"] for d in riyad))
    print("Riyad with B/M anchors:", sum(1 for d in riyad if {a[0] for a in d["anchors"]} & {"B", "M"}),
          " with any anchor:", sum(1 for d in riyad if d["anchors"]))
    print("Ma'alim attrib:", collections.Counter(d["attrib"] for d in maalim))
    print("Ma'alim with B/M anchors:", sum(1 for d in maalim if {a[0] for a in d["anchors"]} & {"B", "M"}))
    print("empty bodies: riyad", sum(1 for d in riyad if not d["body"]), "mishkat", sum(1 for d in mishkat if not d["body"]),
          "maalim", sum(1 for d in maalim if not d["body"]))


if __name__ == "__main__":
    main()
