# Decisions and open questions

## Your standing rules (message of 2026-11-22; they apply to ALL phases, including Ma'alim and Mishkat as the base)

1. **Connectors.** Dropbox for files, GitHub for the whole context (notes, files, everything else), Notion for everything documented (all permissions set to always allow), and "Ummah" for direct hadith references from the six books and Musnad Ahmad.
2. **Grading benchmark.** Arna'ut's grading equals Albani's: if either grades a hadith sahih, it is sahih, even if the other grades it da'if. The benchmark is sahih according to Albani **and/or** Arna'ut. Still report the sahih, da'if and other counts for each scholar separately and combined, and the numbers must add up. Say whether Mahir al-Fahl grades or only gives the sources' grading (answer: he does not grade systematically; see `phase2_report.md` section 3).
3. **Wording-difference rule for comparing editions** (your words): "At least one real wording difference is not always a real difference, even though we can have the numbers for At least one real wording difference, At least 3 real wording differences, will be considered a real difference and further more even At least four real wording difference will be considered a real difference if 90% of the wording matches."
4. **Source-class counts**: in Bukhari and Muslim; outside Bukhari and Muslim; in the six books (siha sitta); outside the six; in Musnad Ahmad only; outside the six and also outside Ahmad; in Muwatta only; outside the six, outside Ahmad and also outside Muwatta.
5. **Evidence for grading** (your words): "what you already have is arnaut's full grading and those of albani from mishkat but you still don't have albani's full grading for riyad, we're good to use the evidence ladder to speak for those in bukhari muslim and muttafaq ilayhi, aswell and as for those for which albani has a note in mishkat, and the few labelled ones in the albani file, you can search up the internet and if you find a place where a complete grading of albani is present, I'll download the file and upload it here". (The assistant's reading: the supplied al-Risalah file holds no Arna'ut gradings, so only Albani's Mishkat notes, the Sahihayn inference and the labelled hadith of the Albani file were available.)
6. **Later idea:** Bulugh al-Maram after Mishkat, once everything else is finished.

## Decisions taken

| # | decision | by | date |
| ---: | --- | --- | --- |
| 1 | Benchmark = sahih per Albani and/or Arna'ut (either is enough) | you | 2026-11-22 |
| 2 | Evidence ladder for Albani's grade: Sahihayn attribution, then his label in the Riyad file, then his label on the matching Mishkat entry, else "ungraded" | you (approved) | 2026-11-22 |
| 3 | Wording rule read as: a real difference needs at least 3 real wording differences when the texts match less than 90%, and at least 4 when they match 90% or more. This is the only reading that keeps both of your clauses meaningful; the full grid is in the Phase 1a report so any other reading can be read off | assistant (please confirm) | 2026-11-23 |
| 4 | F (al-Fahl, 1 to 1896, no gaps) is the master numbering | assistant | 2026-11-21 |
| 5 | Hadith are matched by text, not by printed number | assistant | 2026-11-21 |
| 6 | This repository holds derived files only, not the uploaded books; the Albani footnote column is cut to 200 characters | assistant | 2026-11-23 |

## Open: needs you

1. **Arna'ut's gradings.** The al-Risalah file you uploaded has the text without his footnotes. Upload the footnoted edition (Riyad as-Saliheen, tahqiq Shu'ayb al-Arna'ut, Mu'assasat al-Risalah, with takhrij) as PDF or Shamela text and his grade can be read for every hadith.
2. **A complete Albani grading of Riyad.** None was found online (searches turned up only generic archive.org scans that I could not verify, so there is no link to give). If you find one and upload it, the 160 ungraded hadith and the inferred grades get replaced by his own.
3. **Two grading conflicts** (Albani's explicit label against a Bukhari/Muslim attribution). Both stay sahih in the combined count because the Sahihayn side is sahih: F#947 (Amr ibn al-As, "when you bury me ...", Muslim; Albani: da'if) and F#1021 (Abu al-Darda, the first ten verses of al-Kahf; Albani: first narration sahih, second shadh).
4. **Wording rule.** Confirm the reading in decision 3, or tell me another.
5. **Repository visibility.** The repository is public. Make it private in GitHub settings if you prefer.
6. **Musnad Ahmad** is not available in the Ummah tool, so classes 5 to 8 of the source counts rest on the attributions printed in Riyad, Mishkat and Ma'alim.
7. **Residual error.** About 10% of the 111 sahih hadith clearly left out of Mishkat probably have a counterpart (long hadith containing the excerpt, other Companions' wording). A final pass at the level of the matn would shrink the unresolved group; say if you want it before the quoted numbers are final.

## Next

Phase 3 (Ma'alim as the base against Riyad and Mishkat) and Phase 4 (Mishkat as the base against Riyad and Ma'alim) reuse the statuses already computed in all six directions; they need the Phase 2 evidence ladder for grading each base book's hadith.
