#!/usr/bin/env python3
"""Phase 2 analytics + deliverables (benchmark = sahih per Albani and/or Arna'ut, see phase2_build.py).
Writes everything into /home/claude/outputs/phase2/ and a machine-readable numbers file (phase2_numbers.json).
Run: python3 -I phase2_analyze.py
"""
import collections
import csv
import datetime
import json
import os
import pickle
import re
import sys

sys.path.insert(0, "/home/claude/scripts")
import hm_status  # noqa: E402

D = "/home/claude/work/data/"
OUT = "/home/claude/outputs/phase2/"
os.makedirs(OUT, exist_ok=True)

rows = pickle.load(open(D + "phase2_master.pkl", "rb"))
BYID = {r["id"]: r for r in rows}
mis = {e["num"]: e for e in json.load(open(D + "mishkat.json", encoding="utf-8"))}
mal = {e["seq"]: e for e in json.load(open(D + "maalim.json", encoding="utf-8")) if e["kind"] == "hadith"}
corp = pickle.load(open(D + "corpora.pkl", "rb"))
misC = {d["id"]: d for d in corp["mishkat"]}
malC = {d["id"]: d for d in corp["maalim"]}
cw = {int(r["fahl_number"]): r for r in csv.DictReader(open("/home/claude/outputs/phase1a_numbering_crosswalk.csv", encoding="utf-8-sig")) if (r["fahl_number"] or "").strip().isdigit()}
fahl = json.load(open(D + "riyad_fahl.json", encoding="utf-8"))
own_verdicts = {n for n, p, t in json.load(open(D + "fahl_own_verdicts.json", encoding="utf-8"))}

N = len(rows)
NUM = {}  # machine-readable numbers


def tri(status):
    if status in ("IN_CONFIRMED", "IN_PROBABLE"):
        return "IN"
    if status == "NOT_IN":
        return "OUT"
    return "UNRES"


for r in rows:
    r["M3"] = tri(r["mishkat_status"])
    r["A3"] = tri(r["maalim_status"])
    r["fahl_isnad_note"] = r["id"] in own_verdicts
    r["risalah_no"] = cw.get(r["id"], {}).get("risalah_number_as_printed", "")


def pct(a, b):
    return f"{(100.0 * a / b):.1f}%" if b else "n/a"


# ---------------------------------------------------------------- subsets
SAH = [r for r in rows if r["combined_class"] == "SAHIH"]
HAS = [r for r in rows if r["combined_class"] == "HASAN"]
DAI = [r for r in rows if r["combined_class"] == "DAIF"]
OTH = [r for r in rows if r["combined_class"] == "OTHER"]
UNG = [r for r in rows if r["combined_class"] == "UNGRADED"]
assert len(SAH) + len(HAS) + len(DAI) + len(OTH) + len(UNG) == N
SAH_STRICT = [r for r in rows if r["combined_strict_sahih"]]

SETS = {"ALL": rows, "SAHIH": SAH, "HASAN": HAS, "DAIF": DAI, "OTHER": OTH, "UNGRADED": UNG}


# ---------------------------------------------------------------- text helpers
def clean(t):
    return re.sub(r"\s+", " ", t).strip()


def entry_header(r):
    ch = f"Ch.{r['chapter_no']} {r['chapter']}"
    gr = f"Albani: {r['albani_family']} [{r['albani_rung'].split('_')[0]}]"
    if r["albani_label_used"]:
        gr += f" «{clean(r['albani_label_used'])}»"
    gr += f" | Arna'ut: {r['arnaut_family']} [{r['arnaut_rung'].split('_')[0]}]"
    src = "Sources: " + (",".join(r["sources"]) or "-")
    m = f"Mishkat: {r['mishkat_status']}" + (f" (#{r['mishkat_id']})" if r["mishkat_id"] != "" else "")
    a = f"Ma'alim: {r['maalim_status']}" + (f" (block {r['maalim_id']}, book no. {r['maalim_bookno']})" if r["maalim_id"] != "" else "")
    flag = f"  !! {r['review_flag']}" if r["review_flag"] else ""
    note = "  [al-Fahl footnote: isnad weak]" if r["fahl_isnad_note"] else ""
    return (f"[F#{r['id']} | Risalah no. {r['risalah_no']}] {ch}\n   {gr}\n   {src} | {r['partition'].split('_')[0]}\n   {m} | {a}{flag}{note}")


def nearest_line(r, which):
    tid = r["mishkat_id"] if which == "M" else r["maalim_id"]
    st = r["mishkat_status"] if which == "M" else r["maalim_status"]
    if tid == "" or st in ("NOT_IN", "IN_CONFIRMED"):
        return ""
    if which == "M":
        t = clean(misC[tid]["text"])[:170]
        return f"   closest in Mishkat: #{tid} ({st}, score {r['mishkat_score']}) {t}"
    t = clean(malC[tid]["text"])[:170]
    return f"   closest in Ma'alim: block {tid} ({st}, score {r['maalim_score']}) {t}"


def write_txt(fname, title, intro, items, sections=None, nearest=None):
    """items: list of rows; sections: optional list of (heading, rows)"""
    with open(OUT + fname, "w", encoding="utf-8-sig") as f:
        f.write(title + "\n" + "=" * len(title) + "\n")
        f.write(intro.strip() + "\n\n")
        secs = sections or [("", items)]
        for head, its in secs:
            if head:
                f.write("\n" + "#" * 78 + f"\n## {head}  ({len(its)} hadith)\n" + "#" * 78 + "\n\n")
            for r in its:
                f.write(entry_header(r) + "\n")
                if nearest:
                    nl = nearest_line(r, nearest)
                    if nl:
                        f.write(nl + "\n")
                f.write("   " + clean(r["text"]) + "\n" + "-" * 78 + "\n")
    return len(items) if not sections else sum(len(x[1]) for x in sections)


STATUS_NOTE = ("Benchmark: a hadith counts as SAHIH when Albani and/or Arna'ut grade it sahih (either one is enough). Evidence ladder: "
               "A1/N1 = inferred from Bukhari/Muslim attribution, A2 = Albani's own label in his Riyad file, A3 = Albani's label on the matching Mishkat entry. "
               "Arna'ut's gradings are NOT in the supplied Risalah file, so his side currently rests on rung N1 only.")

# ================================================================= 1. grading counts
def fam_counts(field, subset=rows):
    return collections.Counter(r[field] for r in subset)


alb = fam_counts("albani_family")
arn = fam_counts("arnaut_family")
comb = fam_counts("combined_family")
grp = {
    "SAHIH_label": ["SAHIH", "SAHIHAYN", "SAHIH_LIGHAYRIHI"],
    "SAHIH_inferred": ["SAHIHAYN_INFERRED"],
    "HASAN": ["HASAN", "HASAN_LIGHAYRIHI", "JAYYID", "HASAN_SAHIH"],
    "DAIF": ["DAIF", "MAWDU"],
    "OTHER": ["SHADH", "MIXED", "OTHER", "SAHIH_MURSAL"],
    "UNGRADED": ["UNGRADED"],
}


def gsum(counter, key):
    return sum(counter.get(k, 0) for k in grp[key])


grading_table = {}
for scholar, cnt in (("Albani", alb), ("Arna'ut", arn), ("Combined", comb)):
    g = {k: gsum(cnt, k) for k in grp}
    assert sum(g.values()) == N, (scholar, g)
    g["SAHIH_total"] = g["SAHIH_label"] + g["SAHIH_inferred"]
    grading_table[scholar] = g
NUM["grading"] = grading_table
NUM["albani_families"] = dict(alb)
NUM["combined_families"] = dict(comb)
NUM["albani_rungs"] = dict(collections.Counter(r["albani_rung"] for r in rows))
NUM["strict_sahih_combined"] = len(SAH_STRICT)

# ================================================================= 2. source classes
def src_classes(subset):
    n = len(subset)
    c = collections.Counter(r["partition"].split("_")[0] for r in subset)
    in_bm = c["P1"]
    in_six = c["P1"] + c["P2"]
    res = {
        "total": n,
        "1_in_Bukhari_and_Muslim(either)": in_bm,
        "2_outside_Bukhari_and_Muslim": n - in_bm,
        "3_in_siha_sitta": in_six,
        "4_outside_siha_sitta": n - in_six,
        "5_in_Musnad_Ahmad_only(outside six)": c["P3"],
        "6_outside_six_and_outside_Ahmad": c["P4"] + c["P5"],
        "7_in_Muwatta_only(outside six, outside Ahmad)": c["P4"],
        "8_outside_six_Ahmad_and_Muwatta": c["P5"],
        "extra_in_six_but_not_BM": c["P2"],
    }
    return res


srcs_tab = {k: src_classes(v) for k, v in SETS.items()}
NUM["source_classes"] = srcs_tab
both_bm = sum(1 for r in rows if {"B", "M"} <= set(r["sources"]))
only_b = sum(1 for r in rows if "B" in r["sources"] and "M" not in r["sources"])
only_m = sum(1 for r in rows if "M" in r["sources"] and "B" not in r["sources"])
NUM["BM_split"] = {"both_B_and_M": both_bm, "Bukhari_only": only_b, "Muslim_only": only_m}
book_cnt = collections.Counter()
for r in rows:
    for s in r["sources"]:
        book_cnt[s] += 1
NUM["book_counts_any_mention"] = dict(book_cnt)

# ================================================================= 3. coverage tables
def cover(subset):
    n = len(subset)
    out = {"n": n}
    for tgt, key, st in (("Mishkat", "M3", "mishkat_status"), ("Ma'alim", "A3", "maalim_status")):
        c3 = collections.Counter(r[key] for r in subset)
        cs = collections.Counter(r[st] for r in subset)
        out[tgt] = {"IN": c3["IN"], "OUT": c3["OUT"], "UNRES": c3["UNRES"],
                    "confirmed": cs["IN_CONFIRMED"], "probable": cs["IN_PROBABLE"], "uncertain": cs["UNCERTAIN"],
                    "diff_companion": cs["DIFF_COMPANION"], "not_in": cs["NOT_IN"]}
    cells = collections.Counter((r["M3"], r["A3"]) for r in subset)
    out["cells"] = {f"M:{a}|A:{b}": v for (a, b), v in sorted(cells.items())}
    return out


COV = {k: cover(v) for k, v in SETS.items()}
COV["SAHIH_STRICT"] = cover(SAH_STRICT)
# Sahihayn-based vs non-Sahihayn (sahih set)
sah_bm = [r for r in SAH if r["in_BM"]]
sah_nbm = [r for r in SAH if not r["in_BM"]]
COV["SAHIH_in_BM"] = cover(sah_bm)
COV["SAHIH_outside_BM"] = cover(sah_nbm)
COV["ALL_in_BM"] = cover([r for r in rows if r["in_BM"]])
COV["ALL_outside_BM"] = cover([r for r in rows if not r["in_BM"]])
NUM["coverage"] = COV

# the "benchmark = sahih" cell lists
def cell(subset, m3, a3):
    return [r for r in subset if r["M3"] == m3 and r["A3"] == a3]


S_in_both = cell(SAH, "IN", "IN")
S_M_only = [r for r in SAH if r["M3"] == "IN" and r["A3"] != "IN"]  # in Mishkat, not (confirmed) in Ma'alim
S_A_only = [r for r in SAH if r["A3"] == "IN" and r["M3"] != "IN"]
S_neither = [r for r in SAH if r["M3"] != "IN" and r["A3"] != "IN"]
S_out_M = [r for r in SAH if r["M3"] != "IN"]
S_out_A = [r for r in SAH if r["A3"] != "IN"]
S_out_both_conf = [r for r in SAH if r["M3"] == "OUT" and r["A3"] == "OUT"]
NUM["sahih_cells"] = {
    "in_both": len(S_in_both), "in_Mishkat_not_Maalim(unconfirmed)": len(S_M_only), "in_Maalim_not_Mishkat(unconfirmed)": len(S_A_only),
    "in_neither(unconfirmed in both)": len(S_neither), "left_out_of_Mishkat(unconfirmed)": len(S_out_M), "left_out_of_Maalim(unconfirmed)": len(S_out_A),
    "left_out_of_both_confident(NOT_IN in both)": len(S_out_both_conf),
}

# ================================================================= 4. remaining in Mishkat / Ma'alim
st_MR = hm_status.all_status("mishkat", "riyad")
st_AR = hm_status.all_status("maalim", "riyad")
INSET = ("IN_CONFIRMED", "IN_PROBABLE")
fwd_M_strict = {r["mishkat_id"] for r in rows if r["mishkat_status"] == "IN_CONFIRMED"}
fwd_M_incl = {r["mishkat_id"] for r in rows if r["mishkat_status"] in INSET}
rev_M_strict = {m for m, v in st_MR.items() if v[0] == "IN_CONFIRMED"}
rev_M_incl = {m for m, v in st_MR.items() if v[0] in INSET}
fwd_A_strict = {r["maalim_id"] for r in rows if r["maalim_status"] == "IN_CONFIRMED"}
fwd_A_incl = {r["maalim_id"] for r in rows if r["maalim_status"] in INSET}
rev_A_strict = {m for m, v in st_AR.items() if v[0] == "IN_CONFIRMED"}
rev_A_incl = {m for m, v in st_AR.items() if v[0] in INSET}
rem = {
    "Mishkat_total_entries": len(mis),
    "Mishkat_matched_forward(Riyad->Mishkat)_confirmed": len(fwd_M_strict), "Mishkat_matched_forward_incl_probable": len(fwd_M_incl),
    "Mishkat_matched_reverse(Mishkat->Riyad)_confirmed": len(rev_M_strict), "Mishkat_matched_reverse_incl_probable": len(rev_M_incl),
    "Mishkat_removed_union_confirmed": len(fwd_M_strict | rev_M_strict), "Mishkat_removed_union_incl_probable": len(fwd_M_incl | rev_M_incl),
    "Mishkat_remaining_strict": len(mis) - len(fwd_M_strict | rev_M_strict), "Mishkat_remaining_inclusive": len(mis) - len(fwd_M_incl | rev_M_incl),
    "Maalim_total_hadith_blocks": len(mal),
    "Maalim_matched_forward_confirmed": len(fwd_A_strict), "Maalim_matched_forward_incl_probable": len(fwd_A_incl),
    "Maalim_matched_reverse_confirmed": len(rev_A_strict), "Maalim_matched_reverse_incl_probable": len(rev_A_incl),
    "Maalim_removed_union_confirmed": len(fwd_A_strict | rev_A_strict), "Maalim_removed_union_incl_probable": len(fwd_A_incl | rev_A_incl),
    "Maalim_remaining_strict": len(mal) - len(fwd_A_strict | rev_A_strict), "Maalim_remaining_inclusive": len(mal) - len(fwd_A_incl | rev_A_incl),
}
NUM["remaining"] = rem
removed_M = fwd_M_incl | rev_M_incl
removed_A = fwd_A_incl | rev_A_incl
# numbered Mishkat entries that merely continue a previous one ("ورواه مسلم عن جابر", "وفي رواية ...", takhrij/commentary lines)
# do not open with a narrator; they are separated from 'full' hadith entries so that the remaining counts can be read both ways
OPEN = {"عن", "وعن", "عنه", "وعنه", "عنها", "وعنها", "عنهما", "وعنهما", "عنهم", "وعنهم"}
full_M = {k for k, d in misC.items() if d["full"] and d["full"][0] in OPEN}
full_A = {k for k, d in malC.items() if d["full"] and d["full"][0] in OPEN}
rem.update({
    "Mishkat_entries_opening_with_a_narrator": len(full_M), "Mishkat_continuation_or_note_lines": len(mis) - len(full_M),
    "Mishkat_full_entries_removed_incl_probable": len(full_M & removed_M), "Mishkat_full_entries_remaining_inclusive": len(full_M - removed_M),
    "Mishkat_full_entries_removed_confirmed": len(full_M & (fwd_M_strict | rev_M_strict)), "Mishkat_full_entries_remaining_strict": len(full_M - (fwd_M_strict | rev_M_strict)),
    "Maalim_entries_opening_with_a_narrator": len(full_A), "Maalim_continuation_or_note_blocks": len(mal) - len(full_A),
    "Maalim_full_entries_removed_incl_probable": len(full_A & removed_A), "Maalim_full_entries_remaining_inclusive": len(full_A - removed_A),
    "Maalim_full_entries_removed_confirmed": len(full_A & (fwd_A_strict | rev_A_strict)), "Maalim_full_entries_remaining_strict": len(full_A - (fwd_A_strict | rev_A_strict)),
})
rem_M = [mis[k] for k in sorted(mis) if k not in removed_M]
rem_A = [mal[k] for k in sorted(mal) if k not in removed_A]
NUM["remaining_Mishkat_by_albani_family"] = dict(collections.Counter(e["family"] for e in rem_M))
NUM["all_Mishkat_by_albani_family"] = dict(collections.Counter(e["family"] for e in mis.values()))
NUM["removed_Mishkat_by_albani_family"] = dict(collections.Counter(mis[k]["family"] for k in removed_M if k in mis))
NUM["remaining_Maalim_by_flag"] = dict(collections.Counter((e.get("flags") or "none") for e in rem_A))
NUM["all_Maalim_by_flag"] = dict(collections.Counter((e.get("flags") or "none") for e in mal.values()))

with open(OUT + "phase2_remaining_in_mishkat.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mishkat_no", "entry_kind", "albani_label_in_mishkat", "label_family", "book", "chapter(bab)", "status_vs_riyad", "text_start(200)"])
    for e in rem_M:
        st = st_MR[e["num"]]
        w.writerow([e["num"], "hadith" if e["num"] in full_M else "continuation_or_note", e["label"] or "", e["family"], clean(e["book"] or ""), clean(e["bab"] or ""), st[0], clean(e["text"])[:200]])
with open(OUT + "phase2_remaining_in_maalim.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["maalim_block_no", "entry_kind", "maalim_book_no", "flags", "grade_lines", "chapter", "status_vs_riyad", "text_start(200)"])
    for e in rem_A:
        st = st_AR[e["seq"]]
        w.writerow([e["seq"], "hadith" if e["seq"] in full_A else "continuation_or_note", e["bookno"] or "", e.get("flags") or "", " | ".join(e["grades"]), clean(e["chapter"] or ""), st[0], clean(e["main"])[:200]])

# ================================================================= 5. chapter coverage
chap = collections.defaultdict(list)
for r in rows:
    chap[r["chapter_no"]].append(r)
chap_rows = []
for cno in sorted(chap):
    rs = chap[cno]
    ss = [x for x in rs if x["combined_class"] == "SAHIH"]
    chap_rows.append({
        "chapter_no": cno, "title": rs[0]["chapter"], "n": len(rs), "n_sahih": len(ss),
        "in_Mishkat": sum(1 for x in rs if x["M3"] == "IN"), "out_Mishkat": sum(1 for x in rs if x["M3"] == "OUT"), "unres_Mishkat": sum(1 for x in rs if x["M3"] == "UNRES"),
        "in_Maalim": sum(1 for x in rs if x["A3"] == "IN"), "out_Maalim": sum(1 for x in rs if x["A3"] == "OUT"), "unres_Maalim": sum(1 for x in rs if x["A3"] == "UNRES"),
        "sahih_in_Mishkat": sum(1 for x in ss if x["M3"] == "IN"), "sahih_in_Maalim": sum(1 for x in ss if x["A3"] == "IN"),
        "sahih_left_out_of_both(confident)": sum(1 for x in ss if x["M3"] == "OUT" and x["A3"] == "OUT"),
    })
with open(OUT + "phase2_chapter_coverage.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(chap_rows[0].keys()))
    w.writeheader()
    w.writerows(chap_rows)
NUM["chapters"] = len(chap_rows)
big = [c for c in chap_rows if c["n"] >= 5]
NUM["chapters_n>=5"] = len(big)
low_M = sorted(big, key=lambda c: (c["in_Mishkat"] / c["n"], -c["n"]))[:8]
low_A = sorted(big, key=lambda c: (c["in_Maalim"] / c["n"], -c["n"]))[:8]
NUM["lowest_Mishkat_chapters"] = [(c["chapter_no"], c["title"], c["n"], c["in_Mishkat"]) for c in low_M]
NUM["lowest_Maalim_chapters"] = [(c["chapter_no"], c["title"], c["n"], c["in_Maalim"]) for c in low_A]
NUM["chapters_with_zero_in_Mishkat"] = sum(1 for c in chap_rows if c["in_Mishkat"] == 0)
NUM["chapters_with_zero_in_Maalim"] = sum(1 for c in chap_rows if c["in_Maalim"] == 0)
NUM["chapters_fully_in_Mishkat"] = sum(1 for c in chap_rows if c["in_Mishkat"] == c["n"])
NUM["chapters_fully_in_Maalim"] = sum(1 for c in chap_rows if c["in_Maalim"] == c["n"])

# ================================================================= 6. Riyad repeats
import hm_tiers  # noqa: E402

P = pickle.load(open(D + "pairs_riyad_riyad.pkl", "rb"))
RC = {d["id"]: d for d in corp["riyad"]}
par = {i: i for i in RC}


def find(x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


rep_pairs = 0
for (a, b), m in P.items():
    if a >= b:
        continue
    cp = hm_tiers.compat(RC[a], RC[b])
    if cp is False:
        continue
    if min(m["cAB"], m["cBA"]) >= 0.85 or (m["cAB"] >= 0.9 and m["cBA"] >= 0.6) or (m["cBA"] >= 0.9 and m["cAB"] >= 0.6):
        par[find(b)] = find(a)
        rep_pairs += 1
cl = collections.Counter(find(i) for i in RC)
NUM["riyad_repeats"] = {"near_identical_pairs": rep_pairs, "distinct_narrations": len(cl), "redundant_entries": N - len(cl)}

# ================================================================= 7. Fahl footnote profile
fn_all = [(h["num"], fn) for h in fahl["hadiths"] for fn in (h.get("footnotes") or [])]
prof = collections.Counter()
for n, fn in fn_all:
    t = clean(fn)
    if t.startswith(("أخرجه", "وأخرجه", "أخرج", "وأخرج")):
        prof["takhrij (sources + numbers)"] += 1
    elif t.startswith("انظر الحديث") and len(t) < 60:
        prof["cross-reference to another Riyad hadith"] += 1
    elif t.startswith(("قال النووي", "قال المصنف")) or "شرح صحيح مسلم" in t[:80]:
        prof["quotes/refers to Nawawi / the author"] += 1
    else:
        prof["language, meaning, commentary, other"] += 1
NUM["fahl_footnotes"] = {"total": len(fn_all), "hadith_with_footnote": len({n for n, _ in fn_all}), "profile": dict(prof),
                          "quote_Tirmidhi_verdict": sum(1 for n, fn in fn_all if re.search(r"وقال الترمذي|قال الترمذي|وقال:\s*[«\"]?حديث", clean(fn)) and clean(fn).startswith(("أخرجه", "وأخرجه"))),
                          "name_Albani": sum(1 for n, fn in fn_all if "الألباني" in fn), "name_Arnaut": sum(1 for n, fn in fn_all if re.search("الأرنؤوط|الأرناؤوط|شعيب", fn)),
                          "own_isnad_weak_notes(hadith)": len(own_verdicts)}

# ================================================================= 8. master CSV + txt lists
cols = ["fahl_no", "risalah_printed_no", "albani_no_in_albani_file", "chapter_no", "chapter_title",
        "combined_class", "combined_family", "albani_family", "albani_rung", "albani_label_used", "mishkat_label_of_matched_entry",
        "arnaut_family", "arnaut_rung", "review_flag", "fahl_own_isnad_weak_note",
        "nawawi_attribution", "in_Bukhari_or_Muslim", "in_siha_sitta", "source_partition", "sources_all", "sources_nawawi", "sources_fahl", "sources_crossbook",
        "mishkat_3state", "mishkat_status", "mishkat_no", "mishkat_score", "maalim_3state", "maalim_status", "maalim_block_no", "maalim_book_no", "maalim_score", "maalim_grade_lines",
        "text"]
with open(OUT + "phase2_master_riyad.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in rows:
        w.writerow([r["id"], r["risalah_no"], r["albani_file_num"], r["chapter_no"], r["chapter"], r["combined_class"], r["combined_family"], r["albani_family"], r["albani_rung"],
                    clean(r["albani_label_used"]), clean(r["mishkat_label"]), r["arnaut_family"], r["arnaut_rung"], r["review_flag"], "Y" if r["fahl_isnad_note"] else "",
                    r["nawawi_attrib"], "Y" if r["in_BM"] else "", "Y" if r["in_six"] else "", r["partition"], ",".join(r["sources"]), ",".join(r["src_nawawi"]), ",".join(r["src_fahl"]),
                    ",".join(sorted(set(r["src_mishkat"]) | set(r["src_maalim"]))), r["M3"], r["mishkat_status"], r["mishkat_id"], r["mishkat_score"],
                    r["A3"], r["maalim_status"], r["maalim_id"], r["maalim_bookno"], r["maalim_score"], r["maalim_grade_lines"], clean(r["text"])])

counts_files = {}
INTRO = STATUS_NOTE + "\nStatuses: IN_CONFIRMED = same hadith found; IN_PROBABLE = probably the same hadith in another narration/abridgement; UNCERTAIN = weaker resemblance; DIFF_COMPANION = same wording but a different Companion (distinct hadith); NOT_IN = nothing comparable found.\n"
counts_files["riyad_sahih_all.txt"] = write_txt("riyad_sahih_all.txt", f"Riyad as-Saliheen: ALL SAHIH hadith (Albani and/or Arna'ut) - {len(SAH)} of {N}", INTRO, SAH)
counts_files["riyad_daif_all.txt"] = write_txt("riyad_daif_all.txt", f"Riyad as-Saliheen: ALL DA'IF hadith (Albani and/or Arna'ut, no sahih verdict from either) - {len(DAI)} of {N}", INTRO, DAI)
counts_files["riyad_hasan_all.txt"] = write_txt("riyad_hasan_all.txt", f"Riyad as-Saliheen: HASAN-level hadith (hasan / hasan li-ghayrihi / jayyid / hasan sahih) - {len(HAS)} of {N}", INTRO, HAS)
counts_files["riyad_other_graded.txt"] = write_txt("riyad_other_graded.txt", f"Riyad as-Saliheen: OTHER verdicts (shadh / mixed / other) - {len(OTH)} of {N}", INTRO, OTH)
counts_files["riyad_ungraded_needs_grading.txt"] = write_txt("riyad_ungraded_needs_grading.txt", f"Riyad as-Saliheen: NOT YET GRADED (no Albani/Arna'ut evidence in the supplied files) - {len(UNG)} of {N}",
                                                            INTRO + "These hadith are not in Bukhari/Muslim by Nawawi's attribution, carry no label in Albani's Riyad file and have no graded counterpart in the Mishkat file.\nUploading Arna'ut's footnoted Riyad (or a complete Albani grading) will settle them.\n", UNG)


def split3(subset, key):
    return [("LEFT OUT - no counterpart found (NOT_IN)", [r for r in subset if r[key] == "OUT"]),
            ("UNRESOLVED - same wording but a different Companion (DIFF_COMPANION)", [r for r in subset if r[key] == "UNRES" and r[("mishkat_status" if key == "M3" else "maalim_status")] == "DIFF_COMPANION"]),
            ("UNRESOLVED - weaker resemblance only (UNCERTAIN)", [r for r in subset if r[key] == "UNRES" and r[("mishkat_status" if key == "M3" else "maalim_status")] == "UNCERTAIN"])]


secM = split3(SAH, "M3")
counts_files["riyad_sahih_left_out_of_mishkat.txt"] = write_txt(
    "riyad_sahih_left_out_of_mishkat.txt", "Sahih Riyad hadith LEFT OUT of Mishkat al-Masabih", INTRO + "Section 1 is the confident list; sections 2-3 need a human look (closest Mishkat entry is shown).\n", [], secM, nearest="M")
secA = split3(SAH, "A3")
counts_files["riyad_sahih_left_out_of_maalim.txt"] = write_txt(
    "riyad_sahih_left_out_of_maalim.txt", "Sahih Riyad hadith LEFT OUT of Ma'alim al-Sunnah", INTRO + "Section 1 is the confident list; sections 2-3 need a human look (closest Ma'alim entry is shown).\n", [], secA, nearest="A")
counts_files["riyad_sahih_left_out_of_both.txt"] = write_txt(
    "riyad_sahih_left_out_of_both.txt", "Sahih Riyad hadith LEFT OUT of BOTH Mishkat and Ma'alim", INTRO + "Section 1 = NOT_IN in both books (confident). Section 2 = not confirmed in either book but at least one side is unresolved.\n", [],
    [("LEFT OUT of both - confident (NOT_IN in both)", S_out_both_conf), ("Not found in either, but unresolved on at least one side", [r for r in S_neither if r not in S_out_both_conf])], nearest=None)
counts_files["riyad_sahih_in_both.txt"] = write_txt("riyad_sahih_in_both.txt", "Sahih Riyad hadith INCLUDED in BOTH Mishkat and Ma'alim", INTRO, S_in_both)
counts_files["riyad_sahih_in_mishkat_not_maalim.txt"] = write_txt(
    "riyad_sahih_in_mishkat_not_maalim.txt", "Sahih Riyad hadith in Mishkat but NOT confirmed in Ma'alim", INTRO, [], [("In Mishkat; Ma'alim: NOT_IN", [r for r in S_M_only if r["A3"] == "OUT"]), ("In Mishkat; Ma'alim unresolved", [r for r in S_M_only if r["A3"] == "UNRES"])], nearest="A")
counts_files["riyad_sahih_in_maalim_not_mishkat.txt"] = write_txt(
    "riyad_sahih_in_maalim_not_mishkat.txt", "Sahih Riyad hadith in Ma'alim but NOT confirmed in Mishkat", INTRO, [], [("In Ma'alim; Mishkat: NOT_IN", [r for r in S_A_only if r["M3"] == "OUT"]), ("In Ma'alim; Mishkat unresolved", [r for r in S_A_only if r["M3"] == "UNRES"])], nearest="M")
NUM["files"] = counts_files
NUM["sahih_cells_detail"] = {
    "in_Mishkat_Maalim_NOT_IN": len([r for r in S_M_only if r["A3"] == "OUT"]), "in_Mishkat_Maalim_UNRES": len([r for r in S_M_only if r["A3"] == "UNRES"]),
    "in_Maalim_Mishkat_NOT_IN": len([r for r in S_A_only if r["M3"] == "OUT"]), "in_Maalim_Mishkat_UNRES": len([r for r in S_A_only if r["M3"] == "UNRES"]),
}
NUM["generated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
json.dump(NUM, open(OUT + "phase2_numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: NUM[k] for k in ("grading", "source_classes", "sahih_cells", "sahih_cells_detail", "remaining", "riyad_repeats", "fahl_footnotes")}, ensure_ascii=False, indent=1)[:9000])
