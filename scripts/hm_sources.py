#!/usr/bin/env python3
"""Per-hadith source-book sets for every Riyad hadith (al-Fahl numbering).

Evidence streams (kept separate so every claim can be audited):
  nawawi : Nawawi's own attribution words inside the Riyad text ("رواه البخاري", "متفق عليه", ...)
  fahl   : al-Fahl's takhrij footnotes ("أخرجه: البخاري 1/ 2 (1)، ومسلم ...") incl. "انظر الحديث (n)" pointers
  mishkat: attribution line of the matched Mishkat entry (same hadith, tiers IN_TEXT only)
  maalim : reference codes of the matched Ma'alim entry (خ م د ت ن جه مي حم ك حب هق ...)

Source codes: B Bukhari, M Muslim, D Abu Dawud, T Tirmidhi, N Nasa'i, J Ibn Majah, A Ahmad, MAL Malik (Muwatta),
              DAR Darimi, HAK Hakim, BAY Bayhaqi, TAB Tabarani, HIB Ibn Hibban, KHZ Ibn Khuzayma, DQ Daraqutni, OTH other named.
Writes /home/claude/work/data/sources.pkl : {riyad_id: {stream: set(codes), 'B_taliq': bool, ...}}
Run: python3 -I hm_sources.py
"""
import collections
import json
import os
import pickle
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnorm import norm_formula  # noqa: E402

D = "/home/claude/work/data/"
ARDIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# (code, regex over NORMALISED text — norm_formula output: no diacritics, alef/ya/ta-marbuta unified)
NAMES = [
    ("B", r"البخاري|البخاريه|للبخاري"),
    ("M", r"مسلم"),
    ("D", r"ابو داود|ابوداود|سنن ابي داود"),
    ("T", r"الترمذي"),
    ("N", r"النسايي|النساي|النسائي"),
    ("J", r"ابن ماجه|ابن ماجة"),
    ("A", r"احمد"),
    ("MAL", r"مالك|الموطا"),
    ("DAR", r"الدارمي"),
    ("HAK", r"الحاكم"),
    ("BAY", r"البيهقي"),
    ("TAB", r"الطبراني"),
    ("HIB", r"ابن حبان"),
    ("KHZ", r"ابن خزيمه"),
    ("DQ", r"الدارقطني"),
    ("OTH", r"ابو يعلي|البزار|الطيالسي|عبد الرزاق|ابن ابي شيبه|الحميدي|ابن السني|ابو نعيم|ابن ابي الدنيا|الدارمي|ابن عدي|العقيلي|ابن جرير|البغوي|الخطيب|ابو عوانه|ابن الجارود|الشافعي"),
]
SINGLE = {
    "البخاري": "B", "البخاريه": "B", "لبخاري": "B", "للبخاري": "B", "مسلم": "M", "الترمذي": "T", "النسايي": "N", "النسائي": "N",
    "احمد": "A", "مالك": "MAL", "الموطا": "MAL", "الدارمي": "DAR", "الحاكم": "HAK", "البيهقي": "BAY", "الطبراني": "TAB",
    "الدارقطني": "DQ", "البزار": "OTH", "الطيالسي": "OTH", "الحميدي": "OTH", "ابوداود": "D", "الشيخان": "BM",
}
BIGRAM = {("ابو", "داود"): "D", ("ابي", "داود"): "D", ("ابن", "ماجه"): "J", ("ابن", "ماجة"): "J", ("ابن", "حبان"): "HIB",
          ("ابن", "خزيمه"): "KHZ", ("ابو", "يعلي"): "OTH", ("عبد", "الرزاق"): "OTH", ("ابو", "نعيم"): "OTH", ("ابن", "السني"): "OTH"}
NARR_PREV = {"بن", "ابن", "ابو", "ابي", "عبد", "ام", "اخي", "ابنه", "جد"}
VERB = re.compile(r"(?<![ء-ي])(?:رواه|رواها|رواهما|رواهم|ورواه|وراه|رواية|روايه|اخرجه|واخرجه|اخرجاه|رويناه|روينا|متفق عليه|اتفقا عليه|لمسلم|للبخاري|رواه الشيخان|في صحيح|في صحيحيهما|في الصحيحين|في سنن|في مسند|في الموطا|في كتاب)(?![ء-ي])")
STOP = re.compile(r"(?:\.|\bقال\b|\bوقال\b|\bباسناد\b|\bبسند\b|\bبهذا\b|\bواسناده\b|\bوهو\b|\bوفي\b|\bوله\b|\bبالفاظ\b|\bبلفظ\b|\bبمعناه\b|\bبنحوه\b|\bاسناده\b|\bفي كتاب\b)")

PAGE_MARK = re.compile(r"⦗[^⦘]*⦘")
FOOT = re.compile(r"\(\d{1,3}\)")


def _strip(t):
    return t[1:] if len(t) > 3 and t[0] in "ولفب" else t


def names_in(span):
    """token-based: whole-word names, optional one-letter conjunction/preposition prefix (و ل ف ب)"""
    toks = span.split()
    out = set()
    for i, t in enumerate(toks):
        prev = toks[i - 1] if i else ""
        cands = [t, _strip(t)]
        # bigram names (ابو داود ...)
        if i + 1 < len(toks):
            for a in cands:
                code = BIGRAM.get((a, toks[i + 1]))
                if code:
                    out.add(code)
        for a in cands:
            code = SINGLE.get(a)
            if code:
                if code in ("M", "A", "MAL") and prev in NARR_PREV:
                    continue
                if code == "BM":
                    out |= {"B", "M"}
                else:
                    out.add(code)
                break
    return out


def nawawi_sources(raw):
    s = norm_formula(PAGE_MARK.sub(" ", FOOT.sub(" ", raw)))
    found, taliq = set(), False
    if "متفق عليه" in s or "اتفقا عليه" in s or re.search(r"\bرواه الشيخان\b", s) or "في الصحيحين" in s:
        found |= {"B", "M"}
    for m in VERB.finditer(s):
        seg = s[m.end(): m.end() + 110]
        cut = STOP.search(seg)
        if cut:
            seg = seg[: cut.start()]
        got = names_in(" " + seg)
        # the verb itself may carry a name ("لمسلم", "للبخاري", "في صحيح مسلم")
        got |= names_in(" " + s[m.start(): m.end()])
        found |= got
        if "B" in got and re.search(r"تعليقا", s[m.end(): m.end() + 140]):
            taliq = True
    return found, taliq


FN_NAMES = [
    ("B", r"البخاري"), ("M", r"مسلم"), ("D", r"أبو داود|أبي داود"), ("T", r"الترمذي"),
    ("N", r"النسائي"), ("J", r"ابن ماجه"), ("A", r"أحمد"), ("MAL", r"مالك"),
    ("DAR", r"الدارمي"), ("HAK", r"الحاكم"), ("BAY", r"البيهقي"), ("TAB", r"الطبراني"),
    ("HIB", r"ابن حبان"), ("KHZ", r"ابن خزيمة"), ("DQ", r"الدارقطني"),
    ("OTH", r"أبو يعلى|البزار|الطيالسي|عبد الرزاق|ابن أبي شيبة|الحميدي|ابن السني|أبو نعيم|ابن أبي الدنيا|ابن الجارود|أبو عوانة|الشافعي|الخطيب|ابن عدي|العقيلي"),
]
FN_RE = [(c, re.compile(p)) for c, p in FN_NAMES]
PTR = re.compile(r"انظر الحديث\s*\(?\s*(\d+)\s*\)?")


FN_FIRST = [
    ("B", r"البخاري"), ("M", r"مسلم"), ("D", r"أبو داود|أبي داود"), ("T", r"الترمذي"),
    ("N", r"النسائي"), ("J", r"ابن ماجه"), ("A", r"أحمد|الإمام أحمد"), ("MAL", r"مالك"),
    ("DAR", r"الدارمي"), ("HAK", r"الحاكم"), ("BAY", r"البيهقي"), ("TAB", r"الطبراني"),
    ("HIB", r"ابن حبان"), ("KHZ", r"ابن خزيمة"), ("DQ", r"الدارقطني"),
    ("OTH", r"أبو يعلى|البزار|الطيالسي|عبد الرزاق|ابن أبي شيبة|الحميدي|ابن السني|أبو نعيم|ابن أبي الدنيا|ابن الجارود|أبو عوانة|الشافعي|الخطيب|ابن عدي|العقيلي|ابن أبي عاصم|الطحاوي|إسماعيل القاضي|ابن المبارك|البغوي|ابن الأعرابي"),
]
FN_RE = [(c, re.compile(r"^(?:و|ف)?(?:" + p + r")(?![ء-ي])")) for c, p in FN_FIRST]
LEAD = re.compile(r"^\s*(?:و?أخرجه|و?أخرجها|و?أخرجهما|و?أخرج[^:،.]{0,40}|و?ورواه|ورواية[^:،.]{0,30}أخرجها)\s*:?\s*")
PTR = re.compile(r"انظر الحديث\s*\(?\s*(\d+)\s*\)?")


def fahl_sources(footnotes):
    found, ptrs = set(), []
    for fn in footnotes or []:
        fn = fn.translate(ARDIG)
        m = PTR.search(fn)
        if m and len(fn) < 60:
            ptrs.append(int(m.group(1)))
            continue
        if not re.match(r"\s*(?:وأخرجه|أخرجه|أخرجها|أخرجهما|وأخرج|أخرج|وهو في|هو في|والحديث في)", fn):
            continue
        for sent in re.split(r"(?<=[.؛])\s+", fn):
            lead_cut = LEAD.sub("", sent, count=1) if LEAD.match(sent) else sent
            for clause in re.split(r"،", lead_cut):
                cl = clause.strip()
                cl2 = re.sub(r"^\s*(?:و?أخرجه|و?أخرجها)\s*:?\s*", "", cl)
                for code, rx in FN_RE:
                    mm = rx.match(cl2)
                    if mm and re.search(r"\d", cl2[: mm.end() + 70]):
                        found.add(code)
                        break
    return found, ptrs


MISHKAT_TAIL = re.compile(r"(?:رواه|رواها|رواهما|رواهم|ورواه|متفق عليه)")


def mishkat_sources(text, family=None):
    s = norm_formula(PAGE_MARK.sub(" ", text))
    found = set()
    if "متفق عليه" in s or family == "SAHIHAYN":
        found |= {"B", "M"}
    for m in re.finditer(r"(?:رواه|رواها|رواهما|رواهم|ورواه|روى|ورويا|ورواهما|رواية|وفي روايه)", s):
        seg = s[m.end(): m.end() + 120]
        cut = re.search(r"(?:\.|\bقال\b|\bوقال\b|\bباسناد\b|\bوفي\b)", seg)
        if cut:
            seg = seg[: cut.start()]
        found |= names_in(" " + seg)
    return found


CODE_MAP = {"خ": "B", "م": "M", "د": "D", "ت": "T", "ن": "N", "س": "N", "جه": "J", "مي": "DAR", "حم": "A", "ك": "HAK", "هق": "BAY", "حب": "HIB", "ط": "TAB"}


def maalim_sources(refs, flags):
    found = set()
    if flags and "ق" in flags:
        found |= {"B", "M"}
    if flags and "خ" in flags:
        found.add("B")
    if flags and "م" in flags:
        found.add("M")
    for r in refs or []:
        r = r.translate(ARDIG)
        for part in re.split(r"[،,/؛;]", r):
            part = part.strip()
            m = re.match(r"^(خ|م|د|ت|ن|س|جه|مي|حم|ك|هق|حب)\s*ـ*\s*[\d]+", part)
            if m:
                found.add(CODE_MAP[m.group(1)])
    return found


def main():
    f = json.load(open(D + "riyad_fahl.json", encoding="utf-8"))
    H = f["hadiths"]
    c = pickle.load(open(D + "corpora.pkl", "rb"))
    cls = pickle.load(open(D + "classif.pkl", "rb"))
    mis_raw = {e["num"]: e for e in json.load(open(D + "mishkat.json", encoding="utf-8"))}
    mal_raw = {e["seq"]: e for e in json.load(open(D + "maalim.json", encoding="utf-8")) if e["kind"] == "hadith"}

    out = {}
    fahl_ptr = {}
    for h in H:
        n, t = nawawi_sources(h["raw"])
        fs, ptrs = fahl_sources(h.get("footnotes"))
        out[h["num"]] = {"nawawi": n, "B_taliq_nawawi": t, "fahl": fs, "mishkat": set(), "maalim": set(), "ptrs": ptrs}
    # resolve pointers (انظر الحديث n) once, two passes for chains
    for _ in range(3):
        for k, v in out.items():
            for p in v["ptrs"]:
                if p in out and p != k:
                    v["fahl"] |= out[p]["fahl"]
    # cross-book evidence (same-hadith matches only)
    good = {"IN_TEXT", "IN_ANCHOR_TEXT", "IN_ANCHOR_ONLY"}
    for rid, (tier, tid, m, ex) in cls[("riyad", "mishkat")].items():
        if tier in good and tid in mis_raw:
            out[rid]["mishkat"] = mishkat_sources(mis_raw[tid]["text"], mis_raw[tid].get("family"))
    for rid, (tier, tid, m, ex) in cls[("riyad", "maalim")].items():
        if tier in good and tid in mal_raw:
            e = mal_raw[tid]
            out[rid]["maalim"] = maalim_sources(e.get("refs"), e.get("flags"))
    pickle.dump(out, open(D + "sources.pkl", "wb"))
    # quick report
    def cnt(stream):
        cc = collections.Counter()
        for v in out.values():
            for x in v[stream]:
                cc[x] += 1
        return cc
    for s in ("nawawi", "fahl", "mishkat", "maalim"):
        print(s, "hadith with >=1 source:", sum(1 for v in out.values() if v[s]), dict(cnt(s).most_common()))
    u = {k: v["nawawi"] | v["fahl"] | v["mishkat"] | v["maalim"] for k, v in out.items()}
    print("union with >=1 source:", sum(1 for v in u.values() if v), "of", len(u))
    print("none at all:", [k for k, v in u.items() if not v][:30])


if __name__ == "__main__":
    main()
