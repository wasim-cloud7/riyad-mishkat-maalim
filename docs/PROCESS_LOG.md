# Process log

What was done, in order, and every problem found with how it was handled. Dates are the session dates (Asia/Karachi / America/New_York overlap).

## 2026-11-19 / 20: Phase 1

1. Unpacked `riyad_azkar_mishkat_shamail.zip` and listed every file: two Riyad as-Saliheen editions (al-Fahl; al-Risalah / Arna'ut), Albani's tahqeeq file for Riyad, Mishkat al-Masabih (three files), the Ma'alim text, plus Nawawi's Adhkar and Tirmidhi's Shama'il files (not used in this project).
2. Converted the HTML exports to page-delimited text, keeping page numbers and footnotes (`html2txt.py`).
3. Split F and R into chapters and hadith (F: 372 chapters, 1,896 hadith; R: 372 chapters, 1,893 blocks) (`riyad_parse.py`).
4. Aligned F and R by text, chapter by chapter, then once across chapters for leftovers (`riyad_align.py`); compared every aligned pair word by word and classified each difference (`riyad_compare.py`).
5. Parsed the Albani file into 99 entries (2 front-matter pages, 3 chapter-heading notes, 94 hadith pages), matched the 94 to F by text and measured how his numbering drifts (+1 to +9) (`albani_parse.py`). The gate "sahih + da'if add up to the Riyad total" failed: 22 sahih-type + 54 da'if = 76.
6. Wrote the Phase 1a and 1b reports (`phase1_outputs.py`) and the first Notion pages.

## 2026-11-21: Phase 2, first run

7. Parsed Mishkat (6,283 numbered entries: 6,013 open with a narrator, 270 are note or continuation lines) and Ma'alim (3,373 blocks: 3,354 open with a narrator).
8. Built comparable corpora, matched all six directions between the three books by text, derived the source-book sets, built the Phase 2 master table and analytics.
9. Opened the Notion decision page "how to define 'sahih according to Albani'" (recommended: the evidence ladder). The mapping does not depend on that answer, so it ran meanwhile.

## 2026-11-22: your standing rules arrived

10. Connectors added (Dropbox, GitHub, Notion, Ummah). Arna'ut's grading counts like Albani's; sahih if either says sahih. Per-scholar and combined counts, numbers must add up. Wording-difference rule for Phase 1a. Eight source-class counts. Evidence ladder approved. All rules apply to every phase. Exact wording is in `DECISIONS_AND_OPEN_QUESTIONS.md`.

## 2026-11-22 / 23: audit, correction, regeneration

11. A recall audit of the "left out" lists found two faults (see problems 11 and 12 below), fixed them, and recomputed all six directions. Sahih Riyad hadith clearly left out of Mishkat fell from 183 to 111, and out of Ma'alim from 392 to 335.
12. Applied the wording rule to the 1,892 shared Riyad hadith (`phase1a_rule.py`): 294 have at least one real wording difference in the body, 68 at least two, 19 at least three, 10 at least four; 11 meet the rule.
13. Regenerated every Phase 2 file and rewrote the report with the grading tables, source classes and overlaps (`phase2_build.py`, `phase2_analyze.py`, `phase2_report.py`). Checked: the grading tables add to 1,896 for each scholar and combined; the overlap matrix adds to 1,615; the source classes partition as stated.
14. Saved scripts, reports and lists to this repository; wrote the Notion pages and Dropbox copies.

## Problems found and how they were handled

| # | problem | effect | handling |
| ---: | --- | --- | --- |
| 1 | R's printed numbers are unreliable (13 typos, a +1 shift over F#456 to 854, two skipped numbers) | wrong pairing if matched by number | matched by text and sequence, never by printed number |
| 2 | F printed one chapter number wrongly (277 shown as 227) | chapter mismatch | chapters counted in order, not read from the print |
| 3 | F page markers and Qur'an references made 724 hadith look different | inflated differences | stripped before comparing; the real figure is 367 |
| 4 | Spelling conventions and attached connector letters inflated the differences | same | classified separately from real wording differences |
| 5 | Albani repeats some hadith | text matching could pick the wrong copy | containment score plus a position check; one manual placement (Albani #1700 placed at F#1691 and flagged) |
| 6 | Earlier-session faults: stale `classif.pkl` metrics; a regex boundary for "لمسلم"; cross-book Bukhari/Muslim evidence; Bukhari mu'allaq F#1013; a crosswalk filter | small count errors | each fixed when found, outputs regenerated |
| 7 | `phase1a_rule.py` assumed the wrong code for the body zone, so it returned empty results | no numbers | corrected the zone code |
| 8 | Section numbering clash in the Phase 1a report | two sections numbered 6 | the new section is numbered 7 |
| 9 | `phase2_report.py` had f-string quoting errors and a `%` formatting error | script crashed | fixed; two unsupported sentences in the draft were corrected |
| 10 | The Albani file is not a full grading | gate failed | evidence ladder, approved 2026-11-22 |
| 11 | Junk narrator names: Mishkat entries opening with "وعنه" (and from him) inherited names from note lines; Riyad entries opening with an ordinal ("الثامن: عنه") had no narrator | identical hadith treated as a different Companion, so wrongly "left out" | rewrote the name extractor (`hm_names.py`): ordinals skipped, carry-forward only from real named entries, Abu Dharr and Ali recognised |
| 12 | The same hadith in another narration (different wording, shorter or longer) scored low | wrongly "left out" | rescue rules R1 to R4 and one shared status for repeated Riyad hadith (`hm_status.py`) |

## Still open

See `DECISIONS_AND_OPEN_QUESTIONS.md`: Arna'ut's footnoted edition, a complete Albani grading, two grading conflicts (F#947, F#1021), the repository visibility, and Phases 3 and 4.
