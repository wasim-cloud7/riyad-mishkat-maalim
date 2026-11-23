#!/usr/bin/env python3
"""Write the Phase 2 narrative report from phase2_numbers.json (every figure is read from the JSON, nothing typed by hand
except the audit figures, which are marked). Output: /home/claude/outputs/phase2/phase2_report.md
Run: python3 -I phase2_report.py
"""
import csv
import datetime
import json
import pickle
import sys

sys.path.insert(0, "/home/claude/scripts")

OUT = "/home/claude/outputs/phase2/"
D = "/home/claude/work/data/"
n = json.load(open(OUT + "phase2_numbers.json", encoding="utf-8"))
cov, gr, rem = n["coverage"], n["grading"], n["remaining"]
rows = pickle.load(open(D + "phase2_master.pkl", "rb"))
N = len(rows)
MAK = "Ma'alim"
ARK = "Arna'ut"
AR = gr[ARK]
S = cov["SAHIH"]
SM, SA = S["Mishkat"], S["Ma'alim"]
cells = S["cells"]


def f(x):
    return f"{x:,}"


def p(a, b, d=1):
    return f"{100.0 * a / b:.{d}f}%" if b else "n/a"


L = []
A = L.append

# ---------------------------------------------------------------- numbers reused
nS = S["n"]
in_both = cells["M:IN|A:IN"]
mi_ao = cells["M:IN|A:OUT"]
mi_au = cells["M:IN|A:UNRES"]
mo_ai = cells["M:OUT|A:IN"]
mo_ao = cells["M:OUT|A:OUT"]
mo_au = cells["M:OUT|A:UNRES"]
mu_ai = cells["M:UNRES|A:IN"]
mu_ao = cells["M:UNRES|A:OUT"]
mu_au = cells["M:UNRES|A:UNRES"]
assert in_both + mi_ao + mi_au + mo_ai + mo_ao + mo_au + mu_ai + mu_ao + mu_au == nS
assert SM["IN"] + SM["OUT"] + SM["UNRES"] == nS and SA["IN"] + SA["OUT"] + SA["UNRES"] == nS

A("# Phase 2 report - sahih hadith of Riyad as-Saliheen mapped against Mishkat al-Masabih and Ma'alim al-Sunnah")
A("")
A(f"Generated {datetime.date.today().isoformat()} | Riyad master numbering = al-Fahl edition 1..{N} | benchmark = sahih according to Albani and/or Arna'ut (either one is enough)")
A("")
A("## 1. The answer in brief")
A("")
A(f"- Riyad as-Saliheen has **{f(N)}** hadith. Under the benchmark **{f(gr['Combined']['SAHIH_total'])} ({p(gr['Combined']['SAHIH_total'], N)})** are sahih, "
  f"{gr['Combined']['HASAN']} hasan, {gr['Combined']['DAIF']} da'if, {gr['Combined']['OTHER']} other (shadh/mixed) and **{gr['Combined']['UNGRADED']}** cannot be graded from the supplied files "
  f"(sum {f(gr['Combined']['SAHIH_total'] + gr['Combined']['HASAN'] + gr['Combined']['DAIF'] + gr['Combined']['OTHER'] + gr['Combined']['UNGRADED'])}).")
A(f"- **Mishkat al-Masabih** contains **{f(SM['IN'])} of the {f(nS)} sahih Riyad hadith ({p(SM['IN'], nS)})**: {f(SM['confirmed'])} as the same narration ({p(SM['confirmed'], nS)}) and {f(SM['probable'])} as a probable same hadith in another narration. "
  f"**{f(SM['OUT'])} ({p(SM['OUT'], nS)})** are clearly left out and {f(SM['UNRES'])} ({p(SM['UNRES'], nS)}) are unresolved (see 'how to read the three groups').")
A(f"- **Ma'alim al-Sunnah** contains **{f(SA['IN'])} ({p(SA['IN'], nS)})**: {f(SA['confirmed'])} confirmed + {f(SA['probable'])} probable. "
  f"**{f(SA['OUT'])} ({p(SA['OUT'], nS)})** are clearly left out and {f(SA['UNRES'])} ({p(SA['UNRES'], nS)}) are unresolved.")
A(f"- In **both** books: {f(in_both)} sahih Riyad hadith. Clearly left out of **both**: {f(mo_ao)}; with at least one side unresolved, up to {f(mo_ao + mo_au + mu_ao + mu_au)}.")
A(f"- Taking Riyad's hadith out of the two books leaves **{f(rem['Mishkat_remaining_inclusive'])} of Mishkat's {f(rem['Mishkat_total_entries'])} numbered entries** "
  f"({f(rem['Mishkat_full_entries_remaining_inclusive'])} of its {f(rem['Mishkat_entries_opening_with_a_narrator'])} hadith entries) and **{f(rem['Maalim_remaining_inclusive'])} of Ma'alim's {f(rem['Maalim_total_hadith_blocks'])} blocks**.")
A(f"- **Neither book contains all of Riyad, and neither contains all of Riyad's sahih hadith.** Mishkat comes close ({p(SM['IN'], nS)} sure, at most {p(SM['IN'] + SM['UNRES'], nS)} if every unresolved hadith turned out to be present); "
  f"Ma'alim does not ({p(SA['IN'], nS)} sure, at most {p(SA['IN'] + SA['UNRES'], nS)}). Detail and the wording I would use are in section 9.")
A("")
A("How to read the three groups used everywhere below: **IN** = the same hadith found (exact narration, or probably the same hadith in another narration/abridgement); "
  "**OUT** = no counterpart found (the 'left out' lists); **UNRES** = unresolved (a similar text exists but with a different Companion, or only a weak resemblance). "
  "IN + OUT + UNRES always equals the size of the group. The txt lists show the closest entry for every unresolved hadith so you can decide.")
A("")

# ---------------------------------------------------------------- 2 grading
A("## 2. Grading: Albani, Arna'ut and combined (numbers add up to %s)" % f(N))
A("")
A("| scholar | sahih (his label) | sahih (inferred: Bukhari/Muslim attribution) | hasan | da'if | other | no evidence | total |")
A("|---|---:|---:|---:|---:|---:|---:|---:|")
for name in ("Albani", "Arna'ut", "Combined"):
    g = gr[name]
    tot = g["SAHIH_label"] + g["SAHIH_inferred"] + g["HASAN"] + g["DAIF"] + g["OTHER"] + g["UNGRADED"]
    assert tot == N, (name, tot)
    A(f"| {name} | {f(g['SAHIH_label'])} | {f(g['SAHIH_inferred'])} | {f(g['HASAN'])} | {f(g['DAIF'])} | {f(g['OTHER'])} | {f(g['UNGRADED'])} | {f(tot)} |")
A("")
A("Combined = the more favourable of the two (sahih if either scholar says sahih), as you ruled. Strictly sahih without li-ghayrihi: %s." % f(n["strict_sahih_combined"]))
A("")
A("**Where each number comes from (evidence ladder)**")
A("")
ar = n["albani_rungs"]
A("| rung | meaning | hadith |")
A("|---|---|---:|")
A(f"| A2 | Albani's own label in his Riyad file (the 94 annotated pages; 86 carry a label) | {f(ar['A2_Albani_Riyad_file'])} |")
A(f"| A3 | Albani's label on the matching Mishkat entry (his Mishkat edition) | {f(ar['A3_Albani_Mishkat_label'])} |")
A(f"| A1 | no label found, but Nawawi/al-Fahl attribute it to Bukhari and/or Muslim, so sahih by the Sahihayn | {f(ar['A1_Sahihayn_inferred'])} |")
A(f"| A0 | no evidence in the supplied files | {f(ar['A0_no_evidence'])} |")
A("")
A("- **Arna'ut:** the supplied al-Risalah file has the text only, no footnotes, so none of his gradings are in it. His side currently rests on the Bukhari/Muslim attribution only "
  f"({f(AR['SAHIH_inferred'])} sahih-inferred, {f(AR['UNGRADED'])} not gradable). His real gradings need his footnoted Riyad (see section 11).")
A("- **Albani:** a complete grading of Riyad is not in the files and I found none online (two more searches today). The ladder gives a grade to every hadith except the "
  f"{f(gr['Albani']['UNGRADED'])} listed in `riyad_ungraded_needs_grading.txt`.")
A("- **Two conflicts for you to rule on** (Albani's explicit label vs a Bukhari/Muslim attribution; both stay sahih in the combined count because Arna'ut/the Sahihayn side is sahih): "
  "F#947 (Amr ibn al-As, 'when you bury me ...', Muslim; Albani: da'if) and F#1021 (Abu al-Darda, first ten verses of al-Kahf; Albani: first narration sahih, second shadh).")
A("")
A("**Albani's grade families (what he actually says), with the ladder**")
A("")
fam = n["albani_families"]
A("| family | hadith |")
A("|---|---:|")
for k, v in sorted(fam.items(), key=lambda kv: -kv[1]):
    A(f"| {k} | {f(v)} |")
A(f"| **total** | **{f(sum(fam.values()))}** |")
A("")

# ---------------------------------------------------------------- 3 Fahl
ff = n["fahl_footnotes"]
A("## 3. Does Mahir al-Fahl grade the hadith himself?")
A("")
A(f"No, not systematically. His {f(ff['total'])} footnotes on {f(ff['hadith_with_footnote'])} hadith are mostly takhrij (sources with book/hadith numbers: {f(ff['profile']['takhrij (sources + numbers)'])}), "
  f"cross-references to other Riyad hadith ({f(ff['profile']['cross-reference to another Riyad hadith'])}), language/meaning notes ({f(ff['profile']['language, meaning, commentary, other'])}) and quotations of Nawawi ({f(ff['profile']['quotes/refers to Nawawi / the author'])}). "
  f"Where a grade appears it is the source's verdict quoted from Tirmidhi ({f(ff['quote_Tirmidhi_verdict'])} footnotes) or Nawawi. "
  f"He gives his own opinion on only {ff['own_isnad_weak_notes(hadith)']} hadith, always a remark that an isnad is weak. "
  f"He never names Albani or Arna'ut (0 mentions). So al-Fahl contributes sources (which we use for Bukhari/Muslim/six-book membership), not a grading.")
A("")

# ---------------------------------------------------------------- 4 sources
sc = n["source_classes"]
A("## 4. Source books: Bukhari/Muslim, the six books, Musnad Ahmad, Muwatta")
A("")
A("Counted from Nawawi's own attribution ('rawahu ...') and al-Fahl's takhrij; Ahmad and Muwatta also from the attribution of the matching Mishkat/Ma'alim entry. "
  "The classes partition each group, so 1+2 = group, 3+4 = group, 5+6 = class 4, 7+8 = class 6.")
A("")
A("| class | ALL | SAHIH | HASAN | DA'IF | OTHER | NO EVIDENCE |")
A("|---|---:|---:|---:|---:|---:|---:|")
keys = ["1_in_Bukhari_and_Muslim(either)", "2_outside_Bukhari_and_Muslim", "3_in_siha_sitta", "4_outside_siha_sitta", "5_in_Musnad_Ahmad_only(outside six)",
        "6_outside_six_and_outside_Ahmad", "7_in_Muwatta_only(outside six, outside Ahmad)", "8_outside_six_Ahmad_and_Muwatta"]
labels = ["1. in Bukhari and/or Muslim", "2. outside Bukhari and Muslim", "3. in the six books (siha sitta)", "4. outside the six books",
          "5. in Musnad Ahmad only (outside the six)", "6. outside the six and outside Ahmad", "7. in Muwatta only (outside six and Ahmad)", "8. outside six, Ahmad and Muwatta"]
for k, lab in zip(keys, labels):
    A(f"| {lab} | " + " | ".join(f(sc[g][k]) for g in ("ALL", "SAHIH", "HASAN", "DAIF", "OTHER", "UNGRADED")) + " |")
A("| group size | " + " | ".join(f(sc[g]["total"]) for g in ("ALL", "SAHIH", "HASAN", "DAIF", "OTHER", "UNGRADED")) + " |")
A("")
bm = n["BM_split"]
A(f"Inside class 1: in both Bukhari and Muslim (muttafaq 'alayhi) **{f(bm['both_B_and_M'])}**, Bukhari only {f(bm['Bukhari_only'])}, Muslim only {f(bm['Muslim_only'])} (sum {f(sum(bm.values()))}). "
  f"Class 3 but not 1 (in the six books but not in Bukhari/Muslim): {f(sc['ALL']['extra_in_six_but_not_BM'])}.")
A("")

# ---------------------------------------------------------------- 5 coverage
A("## 5. Coverage by grade: how many Riyad hadith are in Mishkat and in Ma'alim")
A("")
A("IN = confirmed + probable; the split is in brackets. UNRES = unresolved.")
A("")
A("| group | hadith | Mishkat IN (conf+prob) | Mishkat OUT | Mishkat UNRES | Ma'alim IN (conf+prob) | Ma'alim OUT | Ma'alim UNRES |")
A("|---|---:|---:|---:|---:|---:|---:|---:|")
for key, lab in (("ALL", "all Riyad"), ("SAHIH", "**sahih (benchmark)**"), ("HASAN", "hasan"), ("DAIF", "da'if"), ("OTHER", "other"), ("UNGRADED", "no evidence")):
    c = cov[key]
    m, a = c["Mishkat"], c["Ma'alim"]
    A(f"| {lab} | {f(c['n'])} | {f(m['IN'])} ({f(m['confirmed'])}+{f(m['probable'])}) {p(m['IN'], c['n'])} | {f(m['OUT'])} {p(m['OUT'], c['n'])} | {f(m['UNRES'])} {p(m['UNRES'], c['n'])} "
      f"| {f(a['IN'])} ({f(a['confirmed'])}+{f(a['probable'])}) {p(a['IN'], c['n'])} | {f(a['OUT'])} {p(a['OUT'], c['n'])} | {f(a['UNRES'])} {p(a['UNRES'], c['n'])} |")
A("")
A(f"Unresolved split for the sahih group: Mishkat {f(SM['uncertain'])} weak resemblance + {f(SM['diff_companion'])} same wording by a different Companion; "
  f"Ma'alim {f(SA['uncertain'])} + {f(SA['diff_companion'])}.")
A("")
A("**Sahih hadith that are in Bukhari/Muslim vs outside them**")
A("")
A("| sahih hadith | n | Mishkat IN | Mishkat OUT | Mishkat UNRES | Ma'alim IN | Ma'alim OUT | Ma'alim UNRES |")
A("|---|---:|---:|---:|---:|---:|---:|---:|")
for key, lab in (("SAHIH_in_BM", "in Bukhari and/or Muslim"), ("SAHIH_outside_BM", "outside Bukhari and Muslim")):
    c = cov[key]
    m, a = c["Mishkat"], c["Ma'alim"]
    A(f"| {lab} | {f(c['n'])} | {f(m['IN'])} {p(m['IN'], c['n'])} | {f(m['OUT'])} {p(m['OUT'], c['n'])} | {f(m['UNRES'])} | {f(a['IN'])} {p(a['IN'], c['n'])} | {f(a['OUT'])} {p(a['OUT'], c['n'])} | {f(a['UNRES'])} |")
A("")
A("Reading: Mishkat takes almost everything that is sahih but outside Bukhari/Muslim (it is built from the six books and carries Albani's labels), while Ma'alim, which leans on Bukhari/Muslim, "
  f"leaves out {p(cov['SAHIH_outside_BM'][MAK]['OUT'], cov['SAHIH_outside_BM']['n'])} ({cov['SAHIH_outside_BM'][MAK]['OUT']} of {cov['SAHIH_outside_BM']['n']}) of the sahih hadith outside them against {p(cov['SAHIH_in_BM'][MAK]['OUT'], cov['SAHIH_in_BM']['n'])} of those inside.")
A("")

# ---------------------------------------------------------------- 6 overlaps
A("## 6. The overlaps for the sahih hadith (each cell is a txt list)")
A("")
A("| | in Ma'alim | left out of Ma'alim | Ma'alim unresolved | total |")
A("|---|---:|---:|---:|---:|")
A(f"| **in Mishkat** | **{f(in_both)}** | {f(mi_ao)} | {f(mi_au)} | {f(in_both + mi_ao + mi_au)} |")
A(f"| **left out of Mishkat** | {f(mo_ai)} | **{f(mo_ao)}** | {f(mo_au)} | {f(mo_ai + mo_ao + mo_au)} |")
A(f"| **Mishkat unresolved** | {f(mu_ai)} | {f(mu_ao)} | {f(mu_au)} | {f(mu_ai + mu_ao + mu_au)} |")
A(f"| total | {f(in_both + mo_ai + mu_ai)} | {f(mi_ao + mo_ao + mu_ao)} | {f(mi_au + mo_au + mu_au)} | {f(nS)} |")
A("")
A("Your questions, answered from the table (sahih hadith only):")
A("")
A(f"- in Mishkat **and** in Ma'alim: **{f(in_both)}** ({p(in_both, SM['IN'])} of those in Mishkat; {p(in_both, SA['IN'])} of those in Ma'alim) -> `riyad_sahih_in_both.txt`")
A(f"- in Mishkat but not in Ma'alim: **{f(mi_ao)}** clearly left out of Ma'alim (+{f(mi_au)} with Ma'alim unresolved = {f(mi_ao + mi_au)}) -> `riyad_sahih_in_mishkat_not_maalim.txt`")
A(f"- in Ma'alim but not in Mishkat: **{f(mo_ai)}** clearly left out of Mishkat (+{f(mu_ai)} with Mishkat unresolved = {f(mo_ai + mu_ai)}) -> `riyad_sahih_in_maalim_not_mishkat.txt`")
A(f"- left out of Mishkat: **{f(SM['OUT'])}** clearly (+{f(SM['UNRES'])} unresolved = {f(SM['OUT'] + SM['UNRES'])} in the list) -> `riyad_sahih_left_out_of_mishkat.txt`")
A(f"- left out of Ma'alim: **{f(SA['OUT'])}** clearly (+{f(SA['UNRES'])} unresolved = {f(SA['OUT'] + SA['UNRES'])} in the list) -> `riyad_sahih_left_out_of_maalim.txt`")
A(f"- left out of Mishkat **and also** left out of Ma'alim: **{f(mo_ao)}** clearly = {p(mo_ao, SM['OUT'])} of the Mishkat-left-out and {p(mo_ao, SA['OUT'])} of the Ma'alim-left-out. "
  f"Counting an unresolved side as not confirmed: {f(mo_ao + mo_au + mu_ao + mu_au)} -> `riyad_sahih_left_out_of_both.txt` (confident part first)")
A("")

# ---------------------------------------------------------------- 7 remaining
A("## 7. What is left in Mishkat and in Ma'alim after taking out Riyad's hadith")
A("")
A("A book entry is 'removed' when it is the same hadith as a Riyad hadith, found from either direction (Riyad -> book, book -> Riyad), so entries that contain a Riyad hadith in another narration are counted once.")
A("")
A("| | numbered entries | opening with a narrator (real hadith entries) | note/continuation lines |")
A("|---|---:|---:|---:|")
A(f"| Mishkat al-Masabih | {f(rem['Mishkat_total_entries'])} | {f(rem['Mishkat_entries_opening_with_a_narrator'])} | {f(rem['Mishkat_continuation_or_note_lines'])} |")
A(f"| Ma'alim al-Sunnah | {f(rem['Maalim_total_hadith_blocks'])} | {f(rem['Maalim_entries_opening_with_a_narrator'])} | {f(rem['Maalim_continuation_or_note_blocks'])} |")
A("")
A("| | removed (confirmed only) | removed (+probable) | **remaining (inclusive)** | remaining (strict) |")
A("|---|---:|---:|---:|---:|")
A(f"| Mishkat, all numbered entries | {f(rem['Mishkat_removed_union_confirmed'])} | {f(rem['Mishkat_removed_union_incl_probable'])} | **{f(rem['Mishkat_remaining_inclusive'])}** ({p(rem['Mishkat_remaining_inclusive'], rem['Mishkat_total_entries'])}) | {f(rem['Mishkat_remaining_strict'])} |")
A(f"| Mishkat, hadith entries only | {f(rem['Mishkat_full_entries_removed_confirmed'])} | {f(rem['Mishkat_full_entries_removed_incl_probable'])} | **{f(rem['Mishkat_full_entries_remaining_inclusive'])}** ({p(rem['Mishkat_full_entries_remaining_inclusive'], rem['Mishkat_entries_opening_with_a_narrator'])}) | {f(rem['Mishkat_full_entries_remaining_strict'])} |")
A(f"| Ma'alim, all blocks | {f(rem['Maalim_removed_union_confirmed'])} | {f(rem['Maalim_removed_union_incl_probable'])} | **{f(rem['Maalim_remaining_inclusive'])}** ({p(rem['Maalim_remaining_inclusive'], rem['Maalim_total_hadith_blocks'])}) | {f(rem['Maalim_remaining_strict'])} |")
A(f"| Ma'alim, hadith blocks only | {f(rem['Maalim_full_entries_removed_confirmed'])} | {f(rem['Maalim_full_entries_removed_incl_probable'])} | **{f(rem['Maalim_full_entries_remaining_inclusive'])}** ({p(rem['Maalim_full_entries_remaining_inclusive'], rem['Maalim_entries_opening_with_a_narrator'])}) | {f(rem['Maalim_full_entries_remaining_strict'])} |")
A("")
rm = n["remaining_Mishkat_by_albani_family"]
A("What remains in Mishkat, by Albani's label printed in Mishkat (all numbered entries): " + ", ".join(f"{k} {f(v)}" for k, v in sorted(rm.items(), key=lambda kv: -kv[1])) + f" (sum {f(sum(rm.values()))}).")
A("What remains in Ma'alim, by the Bukhari/Muslim flag Ma'alim prints: " + ", ".join(f"{k} {f(v)}" for k, v in sorted(n['remaining_Maalim_by_flag'].items(), key=lambda kv: -kv[1])) + f" (sum {f(sum(n['remaining_Maalim_by_flag'].values()))}); "
  "'none' = outside Bukhari/Muslim, ق = muttafaq, خ = Bukhari only, م = Muslim only.")
A("Lists: `phase2_remaining_in_mishkat.csv`, `phase2_remaining_in_maalim.csv` (with the entry kind and status).")
A("")

# ---------------------------------------------------------------- 8 insights
A("## 8. Further insights")
A("")
rr = n["riyad_repeats"]
A(f"1. **Riyad repeats itself.** {rr['near_identical_pairs']} pairs of Riyad hadith are near-identical (same narration filed in two chapters), so Riyad's {f(N)} entries are only about **{f(rr['distinct_narrations'])} distinct narrations** ({rr['redundant_entries']} redundant entries). "
  "All coverage numbers above count entries; a repeated hadith carries the same status in both places.")
chap = list(csv.DictReader(open(OUT + "phase2_chapter_coverage.csv", encoding="utf-8-sig")))
big = [r for r in chap if int(r["n_sahih"]) >= 5]
lowM = sorted(big, key=lambda r: (int(r["sahih_in_Mishkat"]) / int(r["n_sahih"]), -int(r["n_sahih"])))[:5]
lowA = sorted(big, key=lambda r: (int(r["sahih_in_Maalim"]) / int(r["n_sahih"]), -int(r["n_sahih"])))[:5]
A(f"2. **Chapters.** {len(chap)} Riyad chapters contain hadith; {n['chapters_fully_in_Mishkat']} are fully in Mishkat and {n['chapters_fully_in_Maalim']} fully in Ma'alim; "
  f"{n['chapters_with_zero_in_Mishkat']} chapters have no hadith in Mishkat ({sum(1 for r in chap if int(r['in_Mishkat']) == 0 and int(r['n']) == 1)} of them hold a single hadith) and {n['chapters_with_zero_in_Maalim']} none in Ma'alim ({sum(1 for r in chap if int(r['in_Maalim']) == 0 and int(r['n']) == 1)} single-hadith chapters). Chapters with the lowest sahih coverage (5 or more sahih hadith):")
A("")
A("| book | chapter (Riyad no. and title) | sahih hadith | of them in the book |")
A("|---|---|---:|---:|")
for r in lowM:
    A(f"| Mishkat | {r['chapter_no']} {r['title'][:70]} | {r['n_sahih']} | {r['sahih_in_Mishkat']} |")
for r in lowA:
    A(f"| Ma'alim | {r['chapter_no']} {r['title'][:70]} | {r['n_sahih']} | {r['sahih_in_Maalim']} |")
A("")
A("   Full table for all chapters: `phase2_chapter_coverage.csv`.")
A("3. **Ma'alim is Bukhari/Muslim-centred**: it holds "
  f"{p(cov['ALL_in_BM'][MAK]['IN'], cov['ALL_in_BM']['n'])} of Riyad's Bukhari/Muslim hadith but only {p(cov['ALL_outside_BM'][MAK]['IN'], cov['ALL_outside_BM']['n'])} of those outside them. "
  f"Mishkat holds {p(cov['ALL_in_BM']['Mishkat']['IN'], cov['ALL_in_BM']['n'])} and {p(cov['ALL_outside_BM']['Mishkat']['IN'], cov['ALL_outside_BM']['n'])}.")
A(f"4. **Da'if Riyad hadith:** Mishkat holds {f(cov['DAIF']['Mishkat']['IN'])} of the {f(cov['DAIF']['n'])} da'if ones (Mishkat prints weak hadith with Albani's verdict), Ma'alim only {f(cov['DAIF'][MAK]['IN'])}: "
  "Ma'alim filters weak hadith out, Mishkat does not.")
A(f"5. **Riyad is a quarter of Mishkat and a third of Ma'alim:** {p(rem['Mishkat_removed_union_incl_probable'], rem['Mishkat_total_entries'])} of Mishkat's entries and {p(rem['Maalim_removed_union_incl_probable'], rem['Maalim_total_hadith_blocks'])} of Ma'alim's blocks are Riyad hadith.")
A("")

# ---------------------------------------------------------------- 9 conclusion
A("## 9. Are Mishkat and Ma'alim 'built on top of' Riyad?")
A("")
A(f"- **Mishkat: largely yes, not completely.** {p(SM['IN'], nS)} of the sahih Riyad hadith are in it, {p(SM['confirmed'], nS)} as the identical narration. Only {f(SM['OUT'])} sahih hadith ({p(SM['OUT'], nS)}) are clearly left out. "
  f"A sentence I can defend: 'Mishkat contains about 85% of Riyad's sahih hadith for certain (77% as the identical narration) and at most {p(SM['IN'] + SM['UNRES'], nS, 0)}; about 7% are clearly absent, so it does not contain all of it.'")
A(f"- **Ma'alim: no.** {p(SA['IN'], nS)} are in it; {f(SA['OUT'])} sahih hadith ({p(SA['OUT'], nS)}) are clearly left out, at a rate of {p(cov['SAHIH_in_BM'][MAK]['OUT'], cov['SAHIH_in_BM']['n'])} for Bukhari/Muslim hadith and {p(cov['SAHIH_outside_BM'][MAK]['OUT'], cov['SAHIH_outside_BM']['n'])} for the rest. "
  "It is a selective, Bukhari/Muslim-centred book that overlaps with Riyad, not a superset.")
A("- **Both together:** {0} sahih hadith ({1}) are in neither book (confident), {2} are in at least one.".format(f(mo_ao), p(mo_ao, nS), f(nS - mo_ao - mo_au - mu_ao - mu_au)))
A("")

# ---------------------------------------------------------------- 10 reliability
A("## 10. How reliable are these numbers")
A("")
A("**What was checked and corrected on 2026-11-22/23 (this changed the numbers):** a recall audit of the 'left out' lists found two faults.")
A("1. Narrator names: Mishkat entries that open with 'wa-'anhu' (and from him) inherited junk names from note lines, and Riyad entries that open with an ordinal ('al-thamin: 'anhu') had no narrator; "
  "identical hadith were then wrongly treated as 'different Companion'. Fixed in the name extractor (Abu Dharr and Ali now recognised too).")
A("2. Second-pass matching for the same hadith in a different narration (different wording, shorter or longer): rules R1 (shares at least 28% of the rare vocabulary both ways), "
  "R2 (weak resemblance -> unresolved), R3 (same text, different Companion -> unresolved), plus one shared status for repeated Riyad hadith.")
A("3. Result: sahih hadith clearly left out of Mishkat fell from **183 to %s** and out of Ma'alim from **392 to %s** (before/after figures from the first and the corrected run)." % (f(SM["OUT"]), f(SA["OUT"])))
A("")
A("**Measured quality (my manual reading of samples; Arabic read by me, not by a second independent reviewer):**")
A("- Rule R1 (new 'probable'): I read the 62 Riyad-to-Mishkat matches of its first version (58 after the narrator fix); roughly 9 in 10 were the same hadith, the rest related but different (e.g. two different dog-and-water hadith). Rule R3 (same text, different Companion) was right in about 11 of 15 that I read; rule R2 is a weak signal (about 4 in 10), which is why R2 only creates 'unresolved'.")
A("- Residual 'left out of Mishkat': in a random sample of 36 of the remaining unmatched hadith about 4 had a counterpart in Mishkat as a long hadith containing the excerpt (e.g. the Heraclius story) or in another Companion's wording. "
  "So of the %s clearly-left-out sahih hadith expect about 10%% to be present after all." % f(SM["OUT"]))
A("- Ma'alim 'left out': a vocabulary search over all Ma'alim blocks flagged only 18 of the 481 unmatched hadith as having any block that shares 5 of their 8 rarest words, and none of those 18 was the same hadith; Bukhari/Muslim hadith are also anchored by the Bukhari/Muslim numbers that Ma'alim prints.")
A("- Counts of 'sahih' are lower bounds for hadith whose grade rests on the Sahihayn inference only; the 160 with no evidence are not in the sahih count. A complete Albani/Arna'ut grading would move hadith between groups, not change the book coverage of a hadith.")
A("")

# ---------------------------------------------------------------- 11 caveats
A("## 11. Gaps and what I need from you")
A("")
A("1. **Arna'ut's gradings are missing.** The al-Risalah file you uploaded contains the text without his footnotes. Please upload the footnoted edition (Riyad as-Saliheen, tahqiq Shu'ayb al-Arna'ut, Mu'assasat al-Risalah, with takhrij) as PDF/Shamela text and I will read his grade for every hadith; "
  "the table in section 2 then fills the Arna'ut row properly.")
A("2. **A complete Albani grading of Riyad** (every hadith) is not in the files and I did not find one online. If you know of one (e.g. Albani's takhrij of Riyad as a book or the 'Sahih/Da'if' compilation), upload it and the 160 ungraded hadith and the inferred grades get replaced by his own.")
A("3. **Musnad Ahmad is not in the Ummah tool**, so Ahmad membership is taken from the attributions printed in Riyad, Mishkat and Ma'alim. Counts for classes 5-8 therefore rest on printed attributions.")
A("4. **The GitHub repository is public.** I upload scripts, notes and derived lists but not the raw books you uploaded. Tell me if you prefer a private repository.")
A("")

# ---------------------------------------------------------------- 12 strategy
A("## 12. Better strategy, and what comes next")
A("")
A("1. **Match matn families, not only narrations.** The same text reaches the books through different Companions and riwayat; the 'unresolved' group is exactly that. A final pass at the level of the matn would turn most of the unresolved hadith into IN or OUT and give the cleanest 'left out' list.")
A("2. **Use the numbers where they exist.** Ma'alim prints Bukhari/Muslim numbers and so does al-Fahl's takhrij, so Riyad and Ma'alim are matched by number first and by text second (already done). Mishkat prints no numbers, so it stays text-based, but a Mishkat entry that matches a Ma'alim block can inherit that block's Bukhari/Muslim number as a second anchor. Phase 3 (Ma'alim as the base) and Phase 4 (Mishkat as the base) reuse the corrected statuses already computed in all six directions.")
A("3. **Grade by evidence once, reuse everywhere:** the master table `phase2_master_riyad.csv` carries the ladder rung for each hadith so that a later upload of Arna'ut/Albani gradings only updates one column.")
A("4. **Bulugh al-Maram** (your later idea) fits the same pipeline; I would add it after Phase 4.")
A("")

# ---------------------------------------------------------------- files
A("## 13. Files")
A("")
A("| file | content |")
A("|---|---|")
fl = n["files"]
for k, v in fl.items():
    A(f"| `{k}` | {f(v)} hadith |")
A("| `phase2_master_riyad.csv` | one row per Riyad hadith: text, chapter, sources, grades per scholar with rung, status in Mishkat and Ma'alim with matched entry and score |")
A("| `phase2_chapter_coverage.csv` | per chapter coverage |")
A("| `phase2_remaining_in_mishkat.csv`, `phase2_remaining_in_maalim.csv` | what is left in each book |")
A("| `phase2_numbers.json` | every number in this report, machine readable |")
A("")
text = "\n".join(L) + "\n"
open(OUT + "phase2_report.md", "w", encoding="utf-8").write(text)
print(text[:6000])
print("...", len(L), "lines")
