# Riyad as-Saliheen, Mishkat al-Masabih and Ma'alim al-Sunnah: hadith mapping project

Question behind the project: are **Mishkat al-Masabih** and **Ma'alim al-Sunnah** "built on top of" **Riyad as-Saliheen**,
i.e. do they contain all of it, or at least all of its sahih hadith, and how much does each book hold beyond Riyad?
Phases 3 and 4 repeat the test with Ma'alim and then Mishkat as the base book.

Everything here is derived output (scripts, reports, tables, lists). The raw books you uploaded are **not** in this repository.
**This repository is public.** If you prefer the lists to be private, make the repository private in its GitHub settings.

## Status

| phase | question | status |
| --- | --- | --- |
| 1a | Are the two Riyad editions (al-Fahl, al-Arna'ut/al-Risalah) identical? | Done. F = 1,896 hadith, R = 1,892 real hadith. Under the wording rule you set, 11 of the 1,892 shared hadith count as a real difference |
| 1b | Do Albani's sahih + da'if grades add up to the Riyad total? | Gate failed: his file annotates only 94 of 1,896 hadith. Resolved by your approval of an evidence ladder |
| 2 | Which sahih Riyad hadith are in or left out of Mishkat and of Ma'alim? | Done (numbers below). Arna'ut's real gradings are still missing |
| 3 | Ma'alim as the base, against Riyad and Mishkat | Matching statuses for all six directions are computed; the report is not written yet |
| 4 | Mishkat as the base, against Riyad and Ma'alim | Same as phase 3 |
| later | Bulugh al-Maram after Mishkat | Not started (your idea for later) |

## Phase 2 in numbers

Benchmark: a Riyad hadith is sahih when Albani and/or Arna'ut grade it sahih (either one is enough).

| | hadith |
| --- | ---: |
| Riyad (al-Fahl numbering) | 1,896 |
| sahih | 1,615 (85.2%) |
| hasan / da'if / other | 51 / 66 / 4 |
| no evidence in the supplied files | 160 |

| sahih Riyad hadith | in the book | clearly left out | unresolved |
| --- | ---: | ---: | ---: |
| Mishkat al-Masabih | 1,364 (84.5%) | 111 (6.9%) | 140 (8.7%) |
| Ma'alim al-Sunnah | 1,156 (71.6%) | 335 (20.7%) | 124 (7.7%) |

- In both books: 1,038. Clearly left out of both: 57 (133 if an unresolved side counts as not confirmed).
- After taking Riyad's hadith out: 4,771 of Mishkat's 6,283 numbered entries and 2,305 of Ma'alim's 3,373 blocks remain.
- Verdict: neither book contains all of Riyad or all of its sahih hadith. Mishkat comes close, Ma'alim does not.

Full report: [docs/phase2_report.md](docs/phase2_report.md).

## Folder map

| path | content |
| --- | --- |
| `docs/phase2_report.md` | Phase 2 report: grading, source classes, coverage, overlaps, what remains, reliability, gaps |
| `docs/phase1a_editions_comparison_report.txt` | Phase 1a report, including section 7 (your wording rule applied) |
| `docs/phase1b_albani_file_analysis.txt` | Phase 1b report (the Albani file and the evidence-ladder decision) |
| `docs/METHOD.md` | How hadith were matched, the status definitions, the grading ladder |
| `docs/PROCESS_LOG.md` | What was done, in order, with every problem found and how it was fixed |
| `docs/DECISIONS_AND_OPEN_QUESTIONS.md` | Your standing rules, decisions taken, questions that still need you |
| `outputs/phase1/` | Numbering crosswalk, every wording difference, per-hadith rule values, the 94 Albani entries (footnotes cut to 200 characters) |
| `outputs/phase2/riyad_sahih_all.txt` etc. | The txt lists you asked for (all sahih, all da'if, left out of Mishkat, left out of Ma'alim, in both, left out of both, ...) |
| `outputs/phase2/phase2_master_riyad.csv` | One row per Riyad hadith: text, chapter, grades with the rung of evidence, sources, status in Mishkat and Ma'alim |
| `outputs/phase2/phase2_remaining_in_*.csv` | What is left in Mishkat and in Ma'alim after removing Riyad (first 200 characters of each entry) |
| `outputs/phase2/phase2_numbers.json` | Every number in the Phase 2 report, machine readable |
| `scripts/` | The whole pipeline (see below) |
| `data/` | Small numeric files (parse log, comparison summary, wording-rule numbers) |

## Scripts, in the order they ran

The scripts read and write under `/home/claude/work` and `/home/claude/outputs`; change those two paths to rerun elsewhere. The uploaded books are needed as input.

1. `html2txt.py`: HTML exports to page-delimited text.
2. `riyad_parse.py`, `mishkat_parse.py`, `maalim_parse.py`, `albani_parse.py`: parse each book into records.
3. `riyad_align.py`, `riyad_compare.py`, `phase1_outputs.py`, `phase1a_rule.py`: Phase 1a and 1b.
4. `hm_build.py`, `hm_names.py`, `hm_sources.py`: comparable corpora, narrator names, source-book sets.
5. `hm_match.py` (six directions), `hm_classify.py`, `hm_tiers.py`, `hm_status.py`: text matching and final status of each hadith.
6. `phase2_build.py`, `phase2_analyze.py`, `phase2_report.py`: master table, analytics, report.
7. `probe_*.py`, `cmp_chapter_counts.py`, `profile_riyad.py`, `show_chapter.py`, `albani_overview.py`: one-off checks. `hm_status_v1_backup.py` is the status module before the 2026-11-22 correction, kept for the audit trail.

## Things to know before quoting a number

- Arna'ut's gradings are not in the al-Risalah file you uploaded (text only, no footnotes). His side rests on the Bukhari/Muslim attribution only.
- No complete Albani grading of Riyad was found online. His grade comes from the evidence ladder (see `docs/METHOD.md`); 160 hadith have no evidence.
- Matching is by text, not by printed number. About 10% of the 111 sahih hadith clearly left out of Mishkat probably have a counterpart after all (long hadith containing the excerpt, other Companions' wording).
- Musnad Ahmad is not available in the Ummah tool, so Ahmad membership comes from the attributions printed in the books.
