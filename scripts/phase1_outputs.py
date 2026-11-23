#!/usr/bin/env python3
"""Generate Phase 1 deliverables (editions comparison + Albani file analysis) into /home/claude/outputs.

Run: python3 -I phase1_outputs.py
"""
import collections
import csv
import json
import os
import re

D = "/home/claude/work/data/"
OUT = "/home/claude/outputs/"
os.makedirs(OUT, exist_ok=True)

f = json.load(open(D + "riyad_fahl.json", encoding="utf-8"))
r = json.load(open(D + "riyad_risalah.json", encoding="utf-8"))
al = json.load(open(D + "alignment.json", encoding="utf-8"))
cmp_ = json.load(open(D + "compare.json", encoding="utf-8"))
alb = json.load(open(D + "albani.json", encoding="utf-8"))

fnum = {h["num"]: h for h in f["hadiths"]}
rseq = {h["num"]: h for h in r["hadiths"]}
cby = {c["fahl_num"]: c for c in cmp_}
pair_by_fahl = {p["fahl_num"]: p for p in al["pairs"]}


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


# ------------------------------------------------------------------ crosswalk CSV
def expected_printed(n):
    return n + (1 if 456 <= n <= 854 else 0)


typos = []
with open(OUT + "phase1a_numbering_crosswalk.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["fahl_number", "fahl_chapter", "risalah_sequence_in_file", "risalah_number_as_printed", "risalah_chapter",
                "printed_minus_fahl", "text_similarity", "wording_status", "note"])
    for n in sorted(fnum):
        h = fnum[n]
        p = pair_by_fahl.get(n)
        if p is None:
            w.writerow([n, h["chapter"], "", "", "", "", "", "ONLY_IN_FAHL", "no matching hadith text in the Risalah file"])
            continue
        c = cby[n]
        pr = p["risalah_printed"]
        note = ""
        if p.get("moved_chapter"):
            note = f"same hadith, but Risalah files it in chapter {p['chapter_risalah']} (Fahl: chapter {p['chapter']})"
        if isinstance(pr, int) and pr != expected_printed(n):
            t = f"Risalah prints {pr}; true position by text/sequence is {expected_printed(n)} (typo in the printed number)"
            note = (note + "; " if note else "") + t
            typos.append((n, pr, expected_printed(n)))
        w.writerow([n, h["chapter"], p["risalah_seq"], pr, p.get("chapter_risalah", p["chapter"]),
                    (pr - n) if isinstance(pr, int) else "", p["sim"], c["status"], note])
    for y in al["only_risalah"]:
        w.writerow(["", "", y["risalah_seq"], y["risalah_printed"], y["chapter"], "", "", "ONLY_IN_RISALAH",
                    "cross-reference stub at the end of chapter %d (hadith of al-'Irbad, 'already mentioned in the chapter on innovations'); "
                    "Fahl has the same words inside #455, Risalah numbers them separately" % y["chapter"]])

# ------------------------------------------------------------------ wording differences CSV
KIND_LABEL = {
    "different_wording": "WORDING (different word(s))",
    "extra_in_fahl": "EXTRA WORD(S) only in Fahl",
    "extra_in_risalah": "EXTRA WORD(S) only in Risalah",
    "minor_word_form": "MINOR WORD FORM",
    "blessing_formula": "BLESSING FORMULA",
    "connector": "CONNECTOR LETTER (و/ف/ب/ل...)",
    "orth_convention": "SPELLING CONVENTION",
}
ZONE_LABEL = {"Q": "inside quotation marks", "O": "outside quotation marks", "?": "unclear (quotes unbalanced)"}
PART_LABEL = {"H": "BODY (chain + matn)", "T": "TAKHRIJ TAIL (attribution/grading)"}
nrows = 0
with open(OUT + "phase1a_wording_differences.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["fahl_number", "risalah_number_as_printed", "fahl_chapter", "difference_type", "importance", "part_of_hadith",
                "quote_zone", "words_in_Fahl", "words_in_Risalah", "context_Fahl", "context_Risalah"])
    for c in cmp_:
        for d in c["diffs"]:
            imp = ("SUBSTANTIVE" if d["kind"] in ("different_wording", "extra_in_fahl", "extra_in_risalah")
                   else "MINOR" if d["kind"] in ("minor_word_form", "blessing_formula") else "SPELLING ONLY")
            w.writerow([c["fahl_num"], c["risalah_printed"], c["fahl_chapter"], KIND_LABEL[d["kind"]], imp,
                        PART_LABEL[d["hzone"]], ZONE_LABEL[d["zone"]], d["fahl"], d["risalah"], d["ctx_fahl"], d["ctx_risalah"]])
            nrows += 1

# ------------------------------------------------------------------ stats for the report
status = collections.Counter(c["status"] for c in cmp_)
kinds = collections.Counter(d["kind"] for c in cmp_ for d in c["diffs"])
chap = al["chapters"]
chap_diff = [(int(k), v) for k, v in chap.items() if v["fahl"] != v["risalah"]]
sub_body_q = [(c, d) for c in cmp_ for d in c["diffs"]
              if d["kind"] in ("different_wording", "extra_in_fahl", "extra_in_risalah") and d["hzone"] == "H" and d["zone"] == "Q"]
sub_hadith = {c["fahl_num"] for c in cmp_ for d in c["diffs"] if d["kind"] in ("different_wording", "extra_in_fahl", "extra_in_risalah")}
sub_hadith_q = {c["fahl_num"] for c, d in sub_body_q}
tok_f = sum(c["tokens_added_fahl"] for c in cmp_)
tok_r = sum(c["tokens_added_risalah"] for c in cmp_)
ident_exact_after_diac = status["IDENTICAL"]

# pick readable examples: different_wording in the quoted matn of the body
ex = [(c, d) for c, d in sub_body_q if d["kind"] == "different_wording"]
ex.sort(key=lambda t: (-(t[1]["n_fahl"] + t[1]["n_risalah"]), t[0]["fahl_num"]))
examples = ex[:30]

L = []
A = L.append
A("PHASE 1a - COMPARISON OF THE TWO EDITIONS OF RIYAD AS-SALIHEEN")
A("=" * 70)
A("Edition F  = Riyad as-Saliheen, ed. Dr. Mahir Yasin al-Fahl (Dar Ibn Kathir, Damascus/Beirut, 1428 AH / 2007) - file riyad_fahl")
A("Edition R  = Riyad as-Saliheen, ed. Shu'ayb al-Arna'ut (Mu'assasat al-Risalah, 3rd ed., 1419 AH / 1998) - file riyad_risalah")
A("")
A("1. HEADLINE")
A("-" * 70)
A(f"Hadith entries in F: {len(f['hadiths'])}  (numbered 1..1896 with no gaps; 372 chapters)")
A(f"Hadith entries in R: {len(r['hadiths'])} blocks  = {len(al['pairs'])} real hadith + 1 cross-reference stub (see 2e)")
A(f"Matched one-to-one by TEXT (not by printed number): {len(al['pairs'])}")
A(f"In F but not in R: {len(al['only_fahl'])}      In R but not in F: {len(al['only_risalah'])} (stub only)")
A("=> The two files are NOT identical in count: F has 1896 hadith, R has 1892 real hadith (4 fewer).")
A("   Of the 1892 shared hadith, the printed numbers agree except for a +1 shift in F#456-854 and a handful of typos in R (section 3).")
A("")
A("2. THE FIVE STRUCTURAL DIFFERENCES")
A("-" * 70)
A("a) F#855 (chapter 132) - 'ان اولى الناس بالله من بدأهم بالسلام' (Abu Umama). In F this hadith is printed twice, as #855 (ch.132) and #858 (ch.133).")
A("   R prints it once (as #858). So R lacks the first copy of a repeated hadith.")
A("b) F#1374 (chapter 240) - Jabir 'ishtara minhu ba'iran fawazana lahu fa-arjaha' (muttafaq 'alayh): the text is absent from R altogether.")
A("c) F#1375 (chapter 240) - Abu Safwan Suwayd ibn Qays 'jalabtu ana wa-Makhrama al-'Abdi bazzan min Hajar...': absent from R altogether.")
A("   R's printed numbers also skip 1374 and 1375 (1373 is followed by 1376), so the numbering says they exist but the file has no text.")
A("d) F#1749 (chapter 335) - Abu Hurayra 'idha da'a al-rajul imra'atahu ila firashihi fa-abat...' - a repeat of F#281 (chapter 35).")
A("   R prints it once (as #281); the repeat in chapter 335 is absent.")
A("e) R#456 (chapter 54) is not a hadith: it is the closing cross-reference 'hadith al-'Irbad ... wa-qad sabaqa fi bab al-nahy 'an al-bida'.")
A("   F contains exactly the same words at the end of #455 ('wa-fi al-bab ahadith kathira minha: hadith al-'Irbad ...'), unnumbered.")
A("   R numbers it separately, which pushes every later R number up by 1 (F#456..854 = R#457..855) until the missing F#855 absorbs the shift.")
A("")
if al.get("moved_chapter_pairs"):
    for fn, rs, cf, cr in al["moved_chapter_pairs"]:
        A(f"f) Placement: F#{fn} (Abu Mas'ud al-Badri, 'naha 'an thamani al-kalb wa-mahri al-baghiy wa-hulwani al-kahin') is the last hadith of chapter {cf} in F.")
        A(f"   R prints the same hadith with the same number ({fn}) but its text sits before the heading of chapter {cf} (inside chapter {cr}), ahead of #1668-1672. Same hadith, different position in the file.")
    A("")
A("Chapters whose hadith counts differ between F and R: " + ", ".join(f"ch.{k} (F {v['fahl']} / R {v['risalah']})" for k, v in sorted(chap_diff)))
A("")
A("3. NUMBERING IN R (printed numbers vs true position)")
A("-" * 70)
A(f"Printed-number typos in R's file: {len(typos)}")
for n, pr, ex_ in typos:
    A(f"   F#{n}: R prints '{pr}' but its position (by text and sequence) is {ex_}")
A("   (These are typing errors in the Shamela file; the text itself was matched, so they do not affect the comparison.)")
A("")
A("4. WORDING OF THE 1892 SHARED HADITH")
A("-" * 70)
A("Method: both texts stripped of diacritics, punctuation, footnote markers (F), page markers (F) and Qur'an references; compared word by word;")
A("each difference classified. Spelling conventions (e.g. الرحمان/الرحمن, ومئة/ومائة) and attached connector letters are reported separately from real wording differences.")
A("")
A("Hadith by overall status (one status per hadith):")
order = [("IDENTICAL", "identical word for word (diacritics ignored)"),
         ("SPACING_ONLY", "identical words, only word spacing differs (e.g. ما لا / مالا)"),
         ("HAMZA_ALIF_SPELLING_ONLY", "identical except hamza/alif/ya spelling (e.g. أ/ا, ى/ي, ة/ه)"),
         ("ORTHOGRAPHIC_CONVENTIONS_ONLY", "only spelling conventions differ (e.g. الرحمان/الرحمن)"),
         ("CONNECTOR_LETTERS_ONLY", "only attached connector letters (و/ف/ب/ل) and spelling conventions differ"),
         ("BLESSING_FORMULAE_ONLY", "only blessing formulae differ (e.g. تعالى / عز وجل / صلى الله عليه وسلم)"),
         ("WORDING_DIFFERENCES", "at least one real wording difference (different word, extra word or minor word form)")]
for k, desc in order:
    A(f"   {status[k]:5d}  {k:32s} {desc}")
A(f"   {sum(status.values()):5d}  TOTAL")
A("")
A(f"=> {status['IDENTICAL'] + status['SPACING_ONLY']} hadith are word-for-word identical; "
  f"{status['HAMZA_ALIF_SPELLING_ONLY'] + status['ORTHOGRAPHIC_CONVENTIONS_ONLY'] + status['CONNECTOR_LETTERS_ONLY'] + status['BLESSING_FORMULAE_ONLY']} differ only in spelling/connector/blessing; "
  f"{status['WORDING_DIFFERENCES']} contain at least one real wording difference.")
A("")
A("Differences by type (individual differences, all hadith):")
for k in ("different_wording", "extra_in_fahl", "extra_in_risalah", "minor_word_form", "blessing_formula", "connector", "orth_convention"):
    A(f"   {kinds[k]:5d}  {KIND_LABEL[k]}")
A(f"   words present only in F: {tok_f};  words present only in R: {tok_r}")
A(f"   hadith with at least one SUBSTANTIVE difference (different / extra words): {len(sub_hadith)}; of these, inside the quoted prophetic text of the body: {len(sub_hadith_q)}")
A("")
A("Notes on interpretation:")
A("  * 'Extra words' are mostly one-word insertions (the Arabic particle إنّ/إني, هذه, تعالى, a repeated 'قال'): different manuscripts/riwayat followed by each editor.")
A("  * Differences in the TAKHRIJ TAIL (after 'رواه ...') are usually editorial (e.g. 'رواه الترمذي وقال: حديث حسن صحيح' vs a shorter form), not the hadith text.")
A("  * Every difference is listed with its surrounding words in phase1a_wording_differences.csv (filter 'importance' = SUBSTANTIVE).")
A("")
A("5. THE 30 LARGEST WORDING DIFFERENCES INSIDE THE QUOTED MATN (examples)")
A("-" * 70)
for c, d in examples:
    A(f"F#{c['fahl_num']} (R printed {c['risalah_printed']}, ch.{c['fahl_chapter']}):")
    A(f"     F: {d['ctx_fahl']}")
    A(f"     R: {d['ctx_risalah']}")
A("")
A("6. VERDICT FOR PHASE 1a")
A("-" * 70)
A("The two editions contain the same book (1892 hadith in common, in the same order, in the same chapters apart from one boundary case).")
A("They are not literally identical: F has 4 entries that R lacks (2 are repeats of hadith printed twice in F, 2 are absent altogether),")
A("and about 20% of the shared hadith contain at least one real word-level difference, most of them one-word differences between riwayat.")
A("F (1896, clean numbering 1..1896) is the best master numbering for the next phases.")
open(OUT + "phase1a_editions_comparison_report.txt", "w", encoding="utf-8").write("\n".join(L) + "\n")

# ------------------------------------------------------------------ Albani
H = [x for x in alb if x["kind"] == "hadith"]
FAMILY = {
    "ضعيف": "DA'IF (weak)",
    "صحيح": "SAHIH", "صحيح بشواهده": "SAHIH (bi-shawahidihi)", "صحيح لغيره": "SAHIH (li-ghayrihi)", "حسن صحيح": "HASAN SAHIH",
    "حسن": "HASAN", "حسن لغيره": "HASAN (li-ghayrihi)",
    "شاذ": "SHADH", "شاذ بهذا اللفظ": "SHADH (this wording)",
    "الرواية الأولى صحيحة والثانية شاذة": "MIXED (1st narration sahih, 2nd shadh)",
}
lab = collections.Counter(x["label"] for x in H)
with open(OUT + "phase1b_albani_entries.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["albani_number", "albani_page", "mapped_fahl_number", "risalah_number_as_printed", "fahl_chapter",
                "albani_label", "grade_family", "mapping_method", "mapping_score", "hadith_text_start", "albani_footnote"])
    for x in H:
        w.writerow([x["albani_num"], x["page"], x["fahl_num"], x.get("risalah_printed", ""), x["fahl_chapter"], x["label"] or "",
                    FAMILY.get(x["label"], "NO LABEL (comment on a wording/ruling)"), x.get("match_method", ""), x["match_sim"],
                    clean(x["text"])[:160], clean(x["footnote"])])

offs = [(x["albani_num"], x["albani_num"] - x["fahl_num"]) for x in H]
runs = []
for an, o in offs:
    if runs and runs[-1][0] == o:
        runs[-1][2] = an
        runs[-1][3] += 1
    else:
        runs.append([o, an, an, 1])

M = []
B = M.append
B("PHASE 1b - ANALYSIS OF ALBANI'S TAHQEEQ FILE OF RIYAD AS-SALIHEEN")
B("=" * 70)
B("File: 'تحقيق رياض الصالحين للألباني (النووي)', al-Maktab al-Islami, Beirut, 639 pages (page numbers follow the printed edition).")
B("")
B("1. WHAT THE FILE CONTAINS")
B("-" * 70)
npages = len(alb)
B(f"Pages/entries in the file: {npages} (front matter 2, chapter-heading notes {sum(1 for x in alb if x['kind']=='chapter_note')}, hadith pages {len(H)})")
B("Each entry is a PAGE of Albani's edition on which he wrote a footnote. The file does NOT contain the whole book: it holds only the annotated pages.")
B(f"Hadith entries with an Albani footnote: {len(H)}  ({sum(1 for x in H if x['footnote'])} carry a footnote text)")
B(f"Share of Riyad covered: {len(H)} of 1896 hadith = {100*len(H)/1896:.1f}%")
B("")
B("2. ALBANI'S LABELS IN THIS FILE")
B("-" * 70)
for k, v in sorted(lab.items(), key=lambda t: -t[1]):
    B(f"   {v:3d}  {FAMILY.get(k, 'NO LABEL (comment on a wording/ruling)'):45s} [{k or '-'}]")
B(f"   {len(H):3d}  TOTAL")
sahih_like = sum(v for k, v in lab.items() if k and "صحيح" in k and "شاذ" not in k)
B("")
B(f"Explicit sahih-type labels: {sahih_like}   da'if: {lab['ضعيف']}   hasan-type: {lab['حسن'] + lab['حسن لغيره']}   shadh/mixed: {lab['شاذ'] + lab['شاذ بهذا اللفظ'] + lab['الرواية الأولى صحيحة والثانية شاذة']}   unlabeled comments: {lab[None]}")
B("")
B("3. NUMBERING OF ALBANI'S EDITION vs THE TWO EDITIONS")
B("-" * 70)
B("Albani numbers every hadith too; his numbers run ahead of F's by 1 to 9 (offsets below). The file does not say why (probably some narrations or variants carry their own number in his edition) - not verified.")
B("Offset = Albani number - F number, in book order (each run = consecutive annotated hadith with the same offset):")
for o, a_, b_, n in runs:
    B(f"   offset {o:+d}: Albani #{a_}" + (f"..#{b_}" if b_ != a_ else "") + f"  ({n} annotated hadith)")
last = H[-1]
B(f"Last annotated hadith: Albani #{last['albani_num']} = F#{last['fahl_num']} (offset {last['albani_num']-last['fahl_num']:+d}).")
B(f"Inferred total of Albani's numbering = 1896 + {last['albani_num']-last['fahl_num']} = about {1896 + last['albani_num']-last['fahl_num']} (an inference from the offset at the last annotated page, not a count).")
B("Hadith-mapping method: each Albani entry was matched to F by text (containment score >= 0.6, tie-broken by position); all 94 matched.")
B("One entry (Albani #1700, 'al-jaras mizmar al-shaytan') is worded and attributed differently in Albani's edition (Abu Dawud, 'mizmar') than in F and R (Muslim, 'mazamir');")
B("it was placed by position (F#1691) and flagged in the CSV.")
B("")
B("4. THE PHASE 1b TEST: DO SAHIH + DA'IF ADD UP TO THE TOTAL?")
B("-" * 70)
B(f"Hadith in F: 1896.   Albani entries with any label: {len(H)-lab[None]}  (+{lab[None]} unlabeled comments).")
B(f"Sahih ({sahih_like}) + da'if ({lab['ضعيف']}) = {sahih_like + lab['ضعيف']}; with hasan/shadh/mixed: {len(H)-lab[None]}.")
B(f"=> They do not add up to 1896 (they cover {100*(len(H)-lab[None])/1896:.1f}%). Under the rule you set, this is 'problematic'.")
B("")
B("WHY: Albani's edition is a lightly annotated text. He footnotes the hadith he wants to correct or qualify and says nothing about the rest.")
B("His silence is not a grade in this file: the ~1800 unmarked hadith are not labelled sahih in any entry.")
B("")
B("5. CONSEQUENCE FOR PHASE 2 (what has to be decided)")
B("-" * 70)
B("To say which Riyad hadith are 'sahih according to Albani' we need a grade for every hadith. The only Albani-grade evidence inside the supplied files is:")
B("  (1) this file (94 hadith, mostly da'if),")
B("  (2) Mishkat al-Masabih (Albani's edition): footnote grades for every hadith that Mishkat contains and that is not in Bukhari/Muslim,")
B("  (3) Nawawi's own attribution in Riyad: 'muttafaq 'alayh' / 'rawahu al-Bukhari' / 'rawahu Muslim' (the Sahihayn, which Albani treats as sahih).")
B("An 'evidence ladder' built from these gives a defensible sahih / da'if / not-graded split without guessing. See the Phase 2 notes in Notion.")
open(OUT + "phase1b_albani_file_analysis.txt", "w", encoding="utf-8").write("\n".join(M) + "\n")

print("typos in R printed numbers:", len(typos))
print("diff rows:", nrows)
print("status:", dict(status))
print("sub_hadith:", len(sub_hadith), "sub_hadith_q:", len(sub_hadith_q), "chap_diff:", chap_diff)
print("albani runs:", runs[-4:])
