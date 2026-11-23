# Phase 2 report - sahih hadith of Riyad as-Saliheen mapped against Mishkat al-Masabih and Ma'alim al-Sunnah

Generated 2026-11-23 | Riyad master numbering = al-Fahl edition 1..1896 | benchmark = sahih according to Albani and/or Arna'ut (either one is enough)

## 1. The answer in brief

- Riyad as-Saliheen has **1,896** hadith. Under the benchmark **1,615 (85.2%)** are sahih, 51 hasan, 66 da'if, 4 other (shadh/mixed) and **160** cannot be graded from the supplied files (sum 1,896).
- **Mishkat al-Masabih** contains **1,364 of the 1,615 sahih Riyad hadith (84.5%)**: 1,240 as the same narration (76.8%) and 124 as a probable same hadith in another narration. **111 (6.9%)** are clearly left out and 140 (8.7%) are unresolved (see 'how to read the three groups').
- **Ma'alim al-Sunnah** contains **1,156 (71.6%)**: 1,126 confirmed + 30 probable. **335 (20.7%)** are clearly left out and 124 (7.7%) are unresolved.
- In **both** books: 1,038 sahih Riyad hadith. Clearly left out of **both**: 57; with at least one side unresolved, up to 133.
- Taking Riyad's hadith out of the two books leaves **4,771 of Mishkat's 6,283 numbered entries** (4,534 of its 6,013 hadith entries) and **2,305 of Ma'alim's 3,373 blocks**.
- **Neither book contains all of Riyad, and neither contains all of Riyad's sahih hadith.** Mishkat comes close (84.5% sure, at most 93.1% if every unresolved hadith turned out to be present); Ma'alim does not (71.6% sure, at most 79.3%). Detail and the wording I would use are in section 9.

How to read the three groups used everywhere below: **IN** = the same hadith found (exact narration, or probably the same hadith in another narration/abridgement); **OUT** = no counterpart found (the 'left out' lists); **UNRES** = unresolved (a similar text exists but with a different Companion, or only a weak resemblance). IN + OUT + UNRES always equals the size of the group. The txt lists show the closest entry for every unresolved hadith so you can decide.

## 2. Grading: Albani, Arna'ut and combined (numbers add up to 1,896)

| scholar | sahih (his label) | sahih (inferred: Bukhari/Muslim attribution) | hasan | da'if | other | no evidence | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Albani | 1,239 | 374 | 51 | 67 | 5 | 160 | 1,896 |
| Arna'ut | 0 | 1,490 | 0 | 0 | 0 | 406 | 1,896 |
| Combined | 1,239 | 376 | 51 | 66 | 4 | 160 | 1,896 |

Combined = the more favourable of the two (sahih if either scholar says sahih), as you ruled. Strictly sahih without li-ghayrihi: 1,614.

**Where each number comes from (evidence ladder)**

| rung | meaning | hadith |
|---|---|---:|
| A2 | Albani's own label in his Riyad file (the 94 annotated pages; 86 carry a label) | 86 |
| A3 | Albani's label on the matching Mishkat entry (his Mishkat edition) | 1,276 |
| A1 | no label found, but Nawawi/al-Fahl attribute it to Bukhari and/or Muslim, so sahih by the Sahihayn | 374 |
| A0 | no evidence in the supplied files | 160 |

- **Arna'ut:** the supplied al-Risalah file has the text only, no footnotes, so none of his gradings are in it. His side currently rests on the Bukhari/Muslim attribution only (1,490 sahih-inferred, 406 not gradable). His real gradings need his footnoted Riyad (see section 11).
- **Albani:** a complete grading of Riyad is not in the files and I found none online (two more searches today). The ladder gives a grade to every hadith except the 160 listed in `riyad_ungraded_needs_grading.txt`.
- **Two conflicts for you to rule on** (Albani's explicit label vs a Bukhari/Muslim attribution; both stay sahih in the combined count because Arna'ut/the Sahihayn side is sahih): F#947 (Amr ibn al-As, 'when you bury me ...', Muslim; Albani: da'if) and F#1021 (Abu al-Darda, first ten verses of al-Kahf; Albani: first narration sahih, second shadh).

**Albani's grade families (what he actually says), with the ladder**

| family | hadith |
|---|---:|
| SAHIH | 703 |
| SAHIHAYN | 535 |
| SAHIHAYN_INFERRED | 374 |
| UNGRADED | 160 |
| DAIF | 67 |
| HASAN | 39 |
| JAYYID | 7 |
| HASAN_LIGHAYRIHI | 3 |
| HASAN_SAHIH | 2 |
| OTHER | 2 |
| SHADH | 2 |
| MIXED | 1 |
| SAHIH_LIGHAYRIHI | 1 |
| **total** | **1,896** |

## 3. Does Mahir al-Fahl grade the hadith himself?

No, not systematically. His 2,460 footnotes on 1,895 hadith are mostly takhrij (sources with book/hadith numbers: 1,696), cross-references to other Riyad hadith (208), language/meaning notes (438) and quotations of Nawawi (118). Where a grade appears it is the source's verdict quoted from Tirmidhi (120 footnotes) or Nawawi. He gives his own opinion on only 44 hadith, always a remark that an isnad is weak. He never names Albani or Arna'ut (0 mentions). So al-Fahl contributes sources (which we use for Bukhari/Muslim/six-book membership), not a grading.

## 4. Source books: Bukhari/Muslim, the six books, Musnad Ahmad, Muwatta

Counted from Nawawi's own attribution ('rawahu ...') and al-Fahl's takhrij; Ahmad and Muwatta also from the attribution of the matching Mishkat/Ma'alim entry. The classes partition each group, so 1+2 = group, 3+4 = group, 5+6 = class 4, 7+8 = class 6.

| class | ALL | SAHIH | HASAN | DA'IF | OTHER | NO EVIDENCE |
|---|---:|---:|---:|---:|---:|---:|
| 1. in Bukhari and/or Muslim | 1,498 | 1,495 | 0 | 1 | 0 | 2 |
| 2. outside Bukhari and Muslim | 398 | 120 | 51 | 65 | 4 | 158 |
| 3. in the six books (siha sitta) | 1,889 | 1,614 | 51 | 64 | 4 | 156 |
| 4. outside the six books | 7 | 1 | 0 | 2 | 0 | 4 |
| 5. in Musnad Ahmad only (outside the six) | 1 | 0 | 0 | 0 | 0 | 1 |
| 6. outside the six and outside Ahmad | 6 | 1 | 0 | 2 | 0 | 3 |
| 7. in Muwatta only (outside six and Ahmad) | 2 | 1 | 0 | 0 | 0 | 1 |
| 8. outside six, Ahmad and Muwatta | 4 | 0 | 0 | 2 | 0 | 2 |
| group size | 1,896 | 1,615 | 51 | 66 | 4 | 160 |

Inside class 1: in both Bukhari and Muslim (muttafaq 'alayhi) **779**, Bukhari only 210, Muslim only 509 (sum 1,498). Class 3 but not 1 (in the six books but not in Bukhari/Muslim): 391.

## 5. Coverage by grade: how many Riyad hadith are in Mishkat and in Ma'alim

IN = confirmed + probable; the split is in brackets. UNRES = unresolved.

| group | hadith | Mishkat IN (conf+prob) | Mishkat OUT | Mishkat UNRES | Ma'alim IN (conf+prob) | Ma'alim OUT | Ma'alim UNRES |
|---|---:|---:|---:|---:|---:|---:|---:|
| all Riyad | 1,896 | 1,597 (1,446+151) 84.2% | 133 7.0% | 166 8.8% | 1,263 (1,226+37) 66.6% | 481 25.4% | 152 8.0% |
| **sahih (benchmark)** | 1,615 | 1,364 (1,240+124) 84.5% | 111 6.9% | 140 8.7% | 1,156 (1,126+30) 71.6% | 335 20.7% | 124 7.7% |
| hasan | 51 | 50 (50+0) 98.0% | 1 2.0% | 0 0.0% | 27 (26+1) 52.9% | 22 43.1% | 2 3.9% |
| da'if | 66 | 64 (61+3) 97.0% | 1 1.5% | 1 1.5% | 6 (5+1) 9.1% | 51 77.3% | 9 13.6% |
| other | 4 | 4 (4+0) 100.0% | 0 0.0% | 0 0.0% | 0 (0+0) 0.0% | 3 75.0% | 1 25.0% |
| no evidence | 160 | 115 (91+24) 71.9% | 20 12.5% | 25 15.6% | 74 (69+5) 46.2% | 70 43.8% | 16 10.0% |

Unresolved split for the sahih group: Mishkat 60 weak resemblance + 80 same wording by a different Companion; Ma'alim 47 + 77.

**Sahih hadith that are in Bukhari/Muslim vs outside them**

| sahih hadith | n | Mishkat IN | Mishkat OUT | Mishkat UNRES | Ma'alim IN | Ma'alim OUT | Ma'alim UNRES |
|---|---:|---:|---:|---:|---:|---:|---:|
| in Bukhari and/or Muslim | 1,495 | 1,248 83.5% | 111 7.4% | 136 | 1,094 73.2% | 284 19.0% | 117 |
| outside Bukhari and Muslim | 120 | 116 96.7% | 0 0.0% | 4 | 62 51.7% | 51 42.5% | 7 |

Reading: Mishkat takes almost everything that is sahih but outside Bukhari/Muslim (it is built from the six books and carries Albani's labels), while Ma'alim, which leans on Bukhari/Muslim, leaves out 42.5% (51 of 120) of the sahih hadith outside them against 19.0% of those inside.

## 6. The overlaps for the sahih hadith (each cell is a txt list)

| | in Ma'alim | left out of Ma'alim | Ma'alim unresolved | total |
|---|---:|---:|---:|---:|
| **in Mishkat** | **1,038** | 250 | 76 | 1,364 |
| **left out of Mishkat** | 49 | **57** | 5 | 111 |
| **Mishkat unresolved** | 69 | 28 | 43 | 140 |
| total | 1,156 | 335 | 124 | 1,615 |

Your questions, answered from the table (sahih hadith only):

- in Mishkat **and** in Ma'alim: **1,038** (76.1% of those in Mishkat; 89.8% of those in Ma'alim) -> `riyad_sahih_in_both.txt`
- in Mishkat but not in Ma'alim: **250** clearly left out of Ma'alim (+76 with Ma'alim unresolved = 326) -> `riyad_sahih_in_mishkat_not_maalim.txt`
- in Ma'alim but not in Mishkat: **49** clearly left out of Mishkat (+69 with Mishkat unresolved = 118) -> `riyad_sahih_in_maalim_not_mishkat.txt`
- left out of Mishkat: **111** clearly (+140 unresolved = 251 in the list) -> `riyad_sahih_left_out_of_mishkat.txt`
- left out of Ma'alim: **335** clearly (+124 unresolved = 459 in the list) -> `riyad_sahih_left_out_of_maalim.txt`
- left out of Mishkat **and also** left out of Ma'alim: **57** clearly = 51.4% of the Mishkat-left-out and 17.0% of the Ma'alim-left-out. Counting an unresolved side as not confirmed: 133 -> `riyad_sahih_left_out_of_both.txt` (confident part first)

## 7. What is left in Mishkat and in Ma'alim after taking out Riyad's hadith

A book entry is 'removed' when it is the same hadith as a Riyad hadith, found from either direction (Riyad -> book, book -> Riyad), so entries that contain a Riyad hadith in another narration are counted once.

| | numbered entries | opening with a narrator (real hadith entries) | note/continuation lines |
|---|---:|---:|---:|
| Mishkat al-Masabih | 6,283 | 6,013 | 270 |
| Ma'alim al-Sunnah | 3,373 | 3,354 | 19 |

| | removed (confirmed only) | removed (+probable) | **remaining (inclusive)** | remaining (strict) |
|---|---:|---:|---:|---:|
| Mishkat, all numbered entries | 1,293 | 1,512 | **4,771** (75.9%) | 4,990 |
| Mishkat, hadith entries only | 1,278 | 1,479 | **4,534** (75.4%) | 4,735 |
| Ma'alim, all blocks | 1,026 | 1,068 | **2,305** (68.3%) | 2,347 |
| Ma'alim, hadith blocks only | 1,020 | 1,062 | **2,292** (68.3%) | 2,334 |

What remains in Mishkat, by Albani's label printed in Mishkat (all numbered entries): SAHIH 1,543, NOT_STUDIED 1,394, SAHIHAYN 747, DAIF 720, HASAN 234, NO_LABEL 75, JAYYID 28, MAWDU 20, HASAN_SAHIH 6, MAWQUF_MURSAL 3, OTHER 1 (sum 4,771).
What remains in Ma'alim, by the Bukhari/Muslim flag Ma'alim prints: none 1,135, ق 622, م 308, خ 238, خــ 2 (sum 2,305); 'none' = outside Bukhari/Muslim, ق = muttafaq, خ = Bukhari only, م = Muslim only.
Lists: `phase2_remaining_in_mishkat.csv`, `phase2_remaining_in_maalim.csv` (with the entry kind and status).

## 8. Further insights

1. **Riyad repeats itself.** 158 pairs of Riyad hadith are near-identical (same narration filed in two chapters), so Riyad's 1,896 entries are only about **1,749 distinct narrations** (147 redundant entries). All coverage numbers above count entries; a repeated hadith carries the same status in both places.
2. **Chapters.** 366 Riyad chapters contain hadith; 198 are fully in Mishkat and 125 fully in Ma'alim; 13 chapters have no hadith in Mishkat (12 of them hold a single hadith) and 31 none in Ma'alim (25 single-hadith chapters). Chapters with the lowest sahih coverage (5 or more sahih hadith):

| book | chapter (Riyad no. and title) | sahih hadith | of them in the book |
|---|---|---:|---:|
| Mishkat | 282 باب النهي عن تعذيب العبد والدابة والمرأة والولد بغير سبب شرعي أَوْ زائ | 9 | 5 |
| Mishkat | 11 باب في المجاهدة | 17 | 10 |
| Mishkat | 12 باب الحث عَلَى الازدياد من الخير في أواخر العمر | 5 | 3 |
| Mishkat | 59 باب الحث عَلَى الأكل من عمل يده والتعفف به عن السؤال والتعرض للإعطاء | 5 | 3 |
| Mishkat | 62 باب الإيثار والمواساة | 5 | 3 |
| Ma'alim | 78 باب أمر وُلاة الأمور بالرفق برعاياهم ونصيحتهم والشفقة عليهم والنهي عن  | 6 | 2 |
| Ma'alim | 302 باب تحريم النياحة على الميت ولطم الخد وشق الجيب ونتف الشعر وحلقه والدع | 9 | 4 |
| Ma'alim | 80 باب وجوب طاعة ولاة الأمر في غير معصية وتحريم طاعتهم في المعصية | 11 | 5 |
| Ma'alim | 215 باب فضل السواك وخصال الفطرة | 10 | 5 |
| Ma'alim | 36 باب النفقة عَلَى العيال | 8 | 4 |

   Full table for all chapters: `phase2_chapter_coverage.csv`.
3. **Ma'alim is Bukhari/Muslim-centred**: it holds 73.0% of Riyad's Bukhari/Muslim hadith but only 42.5% of those outside them. Mishkat holds 83.4% and 87.4%.
4. **Da'if Riyad hadith:** Mishkat holds 64 of the 66 da'if ones (Mishkat prints weak hadith with Albani's verdict), Ma'alim only 6: Ma'alim filters weak hadith out, Mishkat does not.
5. **Riyad is a quarter of Mishkat and a third of Ma'alim:** 24.1% of Mishkat's entries and 31.7% of Ma'alim's blocks are Riyad hadith.

## 9. Are Mishkat and Ma'alim 'built on top of' Riyad?

- **Mishkat: largely yes, not completely.** 84.5% of the sahih Riyad hadith are in it, 76.8% as the identical narration. Only 111 sahih hadith (6.9%) are clearly left out. A sentence I can defend: 'Mishkat contains about 85% of Riyad's sahih hadith for certain (77% as the identical narration) and at most 93%; about 7% are clearly absent, so it does not contain all of it.'
- **Ma'alim: no.** 71.6% are in it; 335 sahih hadith (20.7%) are clearly left out, at a rate of 19.0% for Bukhari/Muslim hadith and 42.5% for the rest. It is a selective, Bukhari/Muslim-centred book that overlaps with Riyad, not a superset.
- **Both together:** 57 sahih hadith (3.5%) are in neither book (confident), 1,482 are in at least one.

## 10. How reliable are these numbers

**What was checked and corrected on 2026-11-22/23 (this changed the numbers):** a recall audit of the 'left out' lists found two faults.
1. Narrator names: Mishkat entries that open with 'wa-'anhu' (and from him) inherited junk names from note lines, and Riyad entries that open with an ordinal ('al-thamin: 'anhu') had no narrator; identical hadith were then wrongly treated as 'different Companion'. Fixed in the name extractor (Abu Dharr and Ali now recognised too).
2. Second-pass matching for the same hadith in a different narration (different wording, shorter or longer): rules R1 (shares at least 28% of the rare vocabulary both ways), R2 (weak resemblance -> unresolved), R3 (same text, different Companion -> unresolved), plus one shared status for repeated Riyad hadith.
3. Result: sahih hadith clearly left out of Mishkat fell from **183 to 111** and out of Ma'alim from **392 to 335** (before/after figures from the first and the corrected run).

**Measured quality (my manual reading of samples; Arabic read by me, not by a second independent reviewer):**
- Rule R1 (new 'probable'): I read the 62 Riyad-to-Mishkat matches of its first version (58 after the narrator fix); roughly 9 in 10 were the same hadith, the rest related but different (e.g. two different dog-and-water hadith). Rule R3 (same text, different Companion) was right in about 11 of 15 that I read; rule R2 is a weak signal (about 4 in 10), which is why R2 only creates 'unresolved'.
- Residual 'left out of Mishkat': in a random sample of 36 of the remaining unmatched hadith about 4 had a counterpart in Mishkat as a long hadith containing the excerpt (e.g. the Heraclius story) or in another Companion's wording. So of the 111 clearly-left-out sahih hadith expect about 10% to be present after all.
- Ma'alim 'left out': a vocabulary search over all Ma'alim blocks flagged only 18 of the 481 unmatched hadith as having any block that shares 5 of their 8 rarest words, and none of those 18 was the same hadith; Bukhari/Muslim hadith are also anchored by the Bukhari/Muslim numbers that Ma'alim prints.
- Counts of 'sahih' are lower bounds for hadith whose grade rests on the Sahihayn inference only; the 160 with no evidence are not in the sahih count. A complete Albani/Arna'ut grading would move hadith between groups, not change the book coverage of a hadith.

## 11. Gaps and what I need from you

1. **Arna'ut's gradings are missing.** The al-Risalah file you uploaded contains the text without his footnotes. Please upload the footnoted edition (Riyad as-Saliheen, tahqiq Shu'ayb al-Arna'ut, Mu'assasat al-Risalah, with takhrij) as PDF/Shamela text and I will read his grade for every hadith; the table in section 2 then fills the Arna'ut row properly.
2. **A complete Albani grading of Riyad** (every hadith) is not in the files and I did not find one online. If you know of one (e.g. Albani's takhrij of Riyad as a book or the 'Sahih/Da'if' compilation), upload it and the 160 ungraded hadith and the inferred grades get replaced by his own.
3. **Musnad Ahmad is not in the Ummah tool**, so Ahmad membership is taken from the attributions printed in Riyad, Mishkat and Ma'alim. Counts for classes 5-8 therefore rest on printed attributions.
4. **The GitHub repository is public.** I upload scripts, notes and derived lists but not the raw books you uploaded. Tell me if you prefer a private repository.

## 12. Better strategy, and what comes next

1. **Match matn families, not only narrations.** The same text reaches the books through different Companions and riwayat; the 'unresolved' group is exactly that. A final pass at the level of the matn would turn most of the unresolved hadith into IN or OUT and give the cleanest 'left out' list.
2. **Use the numbers where they exist.** Ma'alim prints Bukhari/Muslim numbers and so does al-Fahl's takhrij, so Riyad and Ma'alim are matched by number first and by text second (already done). Mishkat prints no numbers, so it stays text-based, but a Mishkat entry that matches a Ma'alim block can inherit that block's Bukhari/Muslim number as a second anchor. Phase 3 (Ma'alim as the base) and Phase 4 (Mishkat as the base) reuse the corrected statuses already computed in all six directions.
3. **Grade by evidence once, reuse everywhere:** the master table `phase2_master_riyad.csv` carries the ladder rung for each hadith so that a later upload of Arna'ut/Albani gradings only updates one column.
4. **Bulugh al-Maram** (your later idea) fits the same pipeline; I would add it after Phase 4.

## 13. Files

| file | content |
|---|---|
| `riyad_sahih_all.txt` | 1,615 hadith |
| `riyad_daif_all.txt` | 66 hadith |
| `riyad_hasan_all.txt` | 51 hadith |
| `riyad_other_graded.txt` | 4 hadith |
| `riyad_ungraded_needs_grading.txt` | 160 hadith |
| `riyad_sahih_left_out_of_mishkat.txt` | 251 hadith |
| `riyad_sahih_left_out_of_maalim.txt` | 459 hadith |
| `riyad_sahih_left_out_of_both.txt` | 133 hadith |
| `riyad_sahih_in_both.txt` | 1,038 hadith |
| `riyad_sahih_in_mishkat_not_maalim.txt` | 326 hadith |
| `riyad_sahih_in_maalim_not_mishkat.txt` | 118 hadith |
| `phase2_master_riyad.csv` | one row per Riyad hadith: text, chapter, sources, grades per scholar with rung, status in Mishkat and Ma'alim with matched entry and score |
| `phase2_chapter_coverage.csv` | per chapter coverage |
| `phase2_remaining_in_mishkat.csv`, `phase2_remaining_in_maalim.csv` | what is left in each book |
| `phase2_numbers.json` | every number in this report, machine readable |

