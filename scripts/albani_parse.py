#!/usr/bin/env python3
"""Parse Albani's tahqeeq file into entries, map each entry to a Fahl hadith by text, and
analyse the numbering offset.

Outputs /home/claude/work/data/albani.json
Run: python3 -I albani_parse.py
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
al = json.load(open(D + "alignment.json", encoding="utf-8"))

txt = open("/home/claude/work/txt/riyad_albani.txt", encoding="utf-8").read()
blocks = re.split(r"(?m)^=====PAGE (\S+) \| seq (\d+)=====$", txt)
entries = []
for i in range(1, len(blocks), 3):
    page, seq, body = blocks[i], int(blocks[i + 1]), blocks[i + 2].strip()
    entries.append({"page": page, "seq": seq, "body": body})


def fix_albani(s):
    # "رضي الله عن هـ" / "عن ها" / "عن هما" are split by the typist
    s = re.sub(r"(رضي الله عن) (هـ|ها|هما|هم|هن)(?![ء-ي])", r"\1\2", s)
    return s


GRADE_RE = re.compile(r"^(\d+)\s*-\s*(?:\(([^)]*)\))?\s*(.*)$", re.S)
out = []
for e in entries:
    body = e["body"]
    main, _, foot = body.partition("-----FOOTNOTES-----")
    main, foot = main.strip(), foot.strip()
    lines = main.split("\n")
    first = lines[0]
    rec = {"seq": e["seq"], "page": e["page"], "kind": None, "albani_num": None, "label": None, "text": "", "footnote": foot}
    if e["seq"] in (1, 2):
        rec["kind"] = "front_matter"
        rec["text"] = main
    elif first.startswith("العنوان:"):
        rec["kind"] = "chapter_note"
        rec["text"] = first
    else:
        m = re.match(r"^(\d+)\s*-\s*(.*)$", first)
        if not m:
            rec["kind"] = "unparsed"
            rec["text"] = main
        else:
            rec["kind"] = "hadith"
            rec["albani_num"] = int(m.group(1))
            rest = m.group(2).strip()
            lab = re.match(r"^\(([^)]*)\)\s*$", rest)
            if lab:
                rec["label"] = lab.group(1).strip()
                rec["text"] = "\n".join(lines[1:]).strip()
            else:
                rec["label"] = None
                rec["text"] = (rest + "\n" + "\n".join(lines[1:])).strip()
    out.append(rec)

# --- map hadith entries to Fahl by text
for h in f["hadiths"]:
    h["toks"] = norm_formula(re.sub(r"\(\d{1,3}\)", " ", h["raw"])).split()
fnum_map = {h["num"]: h for h in f["hadiths"]}
A_of = {}
cand_map = {}
for rec in out:
    if rec["kind"] != "hadith":
        continue
    toks = norm_formula(fix_albani(rec["text"])).split()
    rec["n_tokens"] = len(toks)
    cands = []
    A = [t for t in toks[:60]]
    A_of[rec["seq"]] = A
    for h in f["hadiths"]:
        sa, sb = set(A), set(h["toks"][:140])
        if not sa or len(sa & sb) / len(sa) < 0.4:
            continue
        # containment of Albani's (shorter) text inside the Fahl block, in order
        mb = difflib.SequenceMatcher(None, A, h["toks"][:140], autojunk=False).get_matching_blocks()
        sc = sum(b.size for b in mb) / max(1, len(A))
        if sc >= 0.6:
            cands.append((sc, h["num"], h["chapter"]))
    cands.sort(reverse=True)
    cand_map[rec["seq"]] = cands
    rec["n_candidates_close"] = sum(1 for c in cands if c[0] >= (cands[0][0] - 0.05)) if cands else 0

# anchors: entries whose best match is unique among close candidates
anchors = []
for rec in out:
    if rec["kind"] == "hadith" and rec["n_candidates_close"] == 1:
        c = cand_map[rec["seq"]][0]
        anchors.append((rec["albani_num"], rec["albani_num"] - c[1]))
anchors.sort()


def expected_offset(an):
    # nearest anchors by Albani number (median of 4 nearest) -> robust local offset
    near = sorted(anchors, key=lambda t: abs(t[0] - an))[:4]
    offs = sorted(o for _, o in near)
    return offs[len(offs) // 2]


for rec in out:
    if rec["kind"] != "hadith":
        continue
    cands = cand_map[rec["seq"]]
    if not cands:
        rec["fahl_num"], rec["match_sim"], rec["fahl_chapter"] = None, 0, None
        continue
    top = cands[0][0]
    close = [c for c in cands if c[0] >= top - 0.05]
    if len(close) == 1:
        pick = close[0]
    else:
        eo = expected_offset(rec["albani_num"])
        pick = min(close, key=lambda c: (abs((rec["albani_num"] - c[1]) - eo), -c[0]))
        rec["ambiguous_candidates"] = [{"fahl": c[1], "sim": round(c[0], 3)} for c in close]
    rec["match_sim"] = round(pick[0], 3)
    rec["fahl_num"] = pick[1]
    rec["fahl_chapter"] = pick[2]
    rec["match_method"] = "text" if len(close) == 1 else "text+offset"
    # sanity: if the chosen hadith sits far from where Albani's own numbering says it should be
    # (repeated hadith, or Albani's edition words it differently), search the expected neighbourhood.
    eo = expected_offset(rec["albani_num"])
    if abs((rec["albani_num"] - pick[1]) - eo) > 3:
        exp = rec["albani_num"] - eo
        bestn, bests = None, -1.0
        for n in range(max(1, exp - 4), min(1896, exp + 4) + 1):
            h = fnum_map[n]
            mb = difflib.SequenceMatcher(None, A_of[rec["seq"]], h["toks"][:140], autojunk=False).get_matching_blocks()
            sc = sum(b.size for b in mb) / max(1, len(A_of[rec["seq"]]))
            if sc > bests:
                bests, bestn = sc, n
        rec["rejected_far_match"] = {"fahl": pick[1], "sim": round(pick[0], 3)}
        rec["match_sim"] = round(bests, 3)
        rec["fahl_num"] = bestn
        rec["fahl_chapter"] = fnum_map[bestn]["chapter"]
        rec["match_method"] = "expected-position search"

# manual overrides (verified by hand): Albani's edition words/attributes this hadith differently from the two
# Riyad editions (مزمار / "رواه أبو داود بإسناد صحيح على شرط مسلم" vs مزامير / "رواه مسلم"), but it sits exactly at
# the position his own numbering predicts (offset +9 -> Fahl #1691).
OVERRIDES = {1700: (1691, "manual: same hadith position (offset +9); Albani edition = مزمار + Abu Dawud attribution, Fahl/Risalah = مزامير + Muslim")}
for rec in out:
    if rec["kind"] == "hadith" and rec["albani_num"] in OVERRIDES:
        n, why = OVERRIDES[rec["albani_num"]]
        rec["fahl_num"], rec["fahl_chapter"], rec["match_method"], rec["override_note"] = n, fnum_map[n]["chapter"], "manual override", why

# risalah number via alignment
f2r = {p["fahl_num"]: p for p in al["pairs"]}
for rec in out:
    if rec.get("fahl_num") in f2r:
        rec["risalah_printed"] = f2r[rec["fahl_num"]]["risalah_printed"]

json.dump(out, open(D + "albani.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

H = [x for x in out if x["kind"] == "hadith"]
print("entries:", len(out), "hadith entries:", len(H), "chapter notes:", sum(1 for x in out if x["kind"] == "chapter_note"), "front:", sum(1 for x in out if x["kind"] == "front_matter"))
print("labels:", collections.Counter(x["label"] for x in H))
low = [x for x in H if x["match_sim"] < 0.6]
print("low-confidence matches:", len(low))
for x in low:
    print("  ", x["albani_num"], x["fahl_num"], x["match_sim"], x["text"][:70].replace("\n", " "))
print("offset (albani - fahl) runs, in Albani order:")
runs = []
for x in H:
    if x["fahl_num"] is None:
        continue
    d = x["albani_num"] - x["fahl_num"]
    if runs and runs[-1][0] == d:
        runs[-1][2] = x["albani_num"]
        runs[-1][3] += 1
    else:
        runs.append([d, x["albani_num"], x["albani_num"], 1])
for d, a, b, n in runs:
    print(f"  offset {d:+d}: Albani #{a}..#{b}  ({n} entries)")
