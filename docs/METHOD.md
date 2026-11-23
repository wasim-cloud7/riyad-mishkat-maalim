# Method

## 1. Texts and numbering

- Riyad as-Saliheen, **F** = ed. Mahir Yasin al-Fahl (Dar Ibn Kathir, 2007): 1,896 hadith, numbered 1 to 1896 with no gaps, 372 chapters. F's numbers are the master numbering ("F#").
- Riyad as-Saliheen, **R** = ed. Shu'ayb al-Arna'ut (Mu'assasat al-Risalah, 3rd ed.): 1,892 real hadith plus one cross-reference stub; its printed numbers contain 13 typos and a +1 shift over F#456 to 854.
- **Albani file**: only the pages of his Riyad edition where he wrote a footnote (94 hadith). His own numbering runs +1 to +9 above F's.
- **Mishkat al-Masabih** (Albani's tahqeeq): 6,283 numbered entries, of which 6,013 open with a narrator and 270 are note or continuation lines. Albani's grade is printed in a bracket on each entry's header line.
- **Ma'alim al-Sunnah** (a Shamela text of numbered entries arranged by topic): 3,373 blocks, of which 3,354 open with a narrator. It prints its own grade lines and source codes such as `[خ8، م16]`.
- Hadith are matched by **text**, never by printed number, because the printed numbers disagree between all the Riyad files.

## 2. Phase 1a: comparing the two Riyad editions

1. Both editions are cut into chapters and hadith, then aligned chapter by chapter with a dynamic-programming alignment on text similarity (`riyad_align.py`); leftovers are aligned once across chapters.
2. Each aligned pair is compared word by word after removing diacritics, punctuation, footnote markers, page markers and Qur'an references (`riyad_compare.py`).
3. Every difference gets one kind: `different_wording`, `extra_in_fahl`, `extra_in_risalah`, `minor_word_form`, `blessing_formula`, `connector` (a one-letter prefix و ف ب ل), `orth_convention` (الرحمان / الرحمن), plus hamza/alif/ya and spacing variants.
4. **Your wording rule** (see `DECISIONS_AND_OPEN_QUESTIONS.md` for your exact words) is applied in `phase1a_rule.py`. A *real wording difference* is a different word, an extra word or a minor word form. Scope used for the headline: the hadith body (chain and matn), not the takhrij tail after "رواه ...". Reading chosen: a hadith pair has a real difference when it has at least 3 real wording differences and the texts match less than 90%, or at least 4 when they match 90% or more. Match % = 100 x (1 - words inside real differences / words in the longer edition's text). The report prints the full grid (at least 1, 2, 3, 4 differences, three scopes, two definitions) so any other reading can be read off.

## 3. Phase 2: matching a Riyad hadith to Mishkat and to Ma'alim

### 3.1 Corpora and retrieval

- `hm_build.py` builds token lists for every entry (Arabic normalisation, light stemming, blessing formulae and takhrij words removed, "main narration" body separated from the takhrij tail) and idf weights over all three books.
- `hm_match.py` retrieves candidates with an idf-weighted index (cosine and containment) and verifies each candidate with `difflib`. Metrics per pair: cAB = share of A's main narration found in order in B, cBA = the same in the other direction, wAB / wBA = idf mass matched, nA / nB = idf mass of each body, bAB / bBA = bag-of-words coverage. Score `S = max(cAB, cBA) + 0.3 x min(cAB, cBA)`.
- Riyad and Ma'alim also share Bukhari/Muslim numbers (Riyad through al-Fahl's takhrij, Ma'alim through its printed codes), used as an anchor for that pair. Mishkat prints no numbers, so it is matched by text only.

### 3.2 Narrator names

`hm_names.py` extracts narrator (Companion) names from the opening of each entry ("عن ..."), carries the name forward for entries that open with "وعنه" (and from him) only from a real named entry, and skips ordinals ("الثامن:"). `compat(A, B)` returns True / False / None (unknown). A pair with `compat = False` can never be the same hadith; it becomes DIFF_COMPANION when the wording is nearly identical.

### 3.3 Tiers and final statuses

First pass (`hm_tiers.classify`): IN_ANCHOR_TEXT, IN_ANCHOR_ONLY, IN_TEXT (S >= 0.75, or both-way coverage >= 0.6), POSSIBLE (S >= 0.55), OTHER_COMPANION (S >= 0.6 with a different Companion), NOT_IN.

Final status (`hm_status.py`):

| status | meaning |
| --- | --- |
| IN_CONFIRMED | same hadith found (text match, or a Bukhari/Muslim number anchor that agrees) |
| IN_PROBABLE | probably the same hadith in another narration or abridgement |
| UNCERTAIN | weaker resemblance only |
| DIFF_COMPANION | nearly identical wording but a different Companion (a distinct hadith, shown separately) |
| NOT_IN | nothing comparable found |

Three-state view used in every table: **IN** = confirmed + probable, **OUT** = NOT_IN, **UNRES** = UNCERTAIN + DIFF_COMPANION. IN + OUT + UNRES always equals the size of the group.

Base rule for IN_PROBABLE: tier POSSIBLE with S >= 0.62, bag-of-words coverage (either direction) >= 0.5 and matched idf mass >= 10. A POSSIBLE pair below that bar is UNCERTAIN; so is a near-miss with 0.45 <= S < 0.62 and a compatible Companion.

Second-pass rescue rules, added on 2026-11-22/23 after a recall audit (`hm_status._rescue`; they only act on narrations the first pass left NOT_IN, or lift UNCERTAIN / DIFF_COMPANION to IN_PROBABLE):

| rule | narrator | condition | result |
| --- | --- | --- | --- |
| R1_bag | same or unknown | S >= 0.30, both bag-of-words coverages >= 0.28 (shared rare vocabulary both ways), matched mass >= 20 | IN_PROBABLE |
| R4_contained | same or unknown | one text at least 75% contained in the other (abridgement), matched mass >= 15, S >= 0.25 | IN_PROBABLE |
| R2_weak | same or unknown | 0.30 <= S < 0.45, matched mass >= 15, at least 35% of one text found in the other | UNCERTAIN |
| R3_other | different | (S >= 0.50 and mass >= 20) or (S >= 0.45 and mass >= 35), at least 40% of one text found in the other | DIFF_COMPANION |

Repeated Riyad hadith (158 near-identical pairs, S >= 0.75 and no narrator contradiction, from `pairs_riyad_riyad`) share one status: the strongest one in the group.

### 3.4 Source books

`hm_sources.py` reads three evidence streams per Riyad hadith and keeps them separate: Nawawi's own attribution ("رواه البخاري", "متفق عليه"), al-Fahl's takhrij footnotes, and (for Ahmad and Muwatta only) the attribution of the matching Mishkat or Ma'alim entry. Codes: B Bukhari, M Muslim, D Abu Dawud, T Tirmidhi, N Nasa'i, J Ibn Majah, A Ahmad, MAL Malik (Muwatta), and others. The eight classes you asked for partition each other: 1+2 = all, 3+4 = all, 5+6 = class 4, 7+8 = class 6.

## 4. Grading: the evidence ladder (approved 2026-11-22)

Your benchmark: sahih according to Albani **and/or** Arna'ut; either is enough. The ladder fills the grade where the supplied files hold none:

| rung | evidence | hadith |
| --- | --- | ---: |
| A2 | Albani's own label in his Riyad file (94 annotated pages; 86 carry a label) | 86 |
| A3 | Albani's label on the matching Mishkat entry (IN_CONFIRMED only) | 1,276 |
| A1 | no label, but Nawawi/al-Fahl attribute the hadith to Bukhari and/or Muslim, so sahih by the Sahihayn | 374 |
| A0 | no evidence in the supplied files | 160 |
| N1 | Arna'ut side: the same Sahihayn inference (the supplied al-Risalah text has no footnotes) | 1,490 sahih, 406 not gradable |

Combined = the more favourable family of the two scholars. Albani's grade families are folded as: sahih = SAHIH, SAHIH_LIGHAYRIHI, SAHIHAYN, SAHIHAYN_INFERRED; hasan = HASAN, HASAN_LIGHAYRIHI, JAYYID, HASAN_SAHIH; da'if = DAIF, MAWDU; other = SHADH, MIXED, OTHER, SAHIH_MURSAL. A later upload of Arna'ut's or Albani's real gradings changes one column in `phase2_master_riyad.csv`, not the book coverage of a hadith.

Does al-Fahl grade? No, not systematically: 2,460 footnotes on 1,895 hadith are mostly takhrij; where a grade appears it is the source's own verdict (for example Tirmidhi's). He gives his own opinion on 44 hadith (a remark that an isnad is weak) and never names Albani or Arna'ut.

## 5. What remains in Mishkat and Ma'alim

A book entry is "removed" when it is the same hadith as a Riyad hadith, found from either direction (Riyad to book, book to Riyad), so an entry that holds a Riyad hadith in another narration is counted once. The report gives the numbers for all numbered entries and for hadith entries only, strict (confirmed) and inclusive (confirmed + probable).

## 6. Known limits

- A random sample of 36 of the unmatched hadith showed about 4 with a counterpart in Mishkat (as a long hadith containing the excerpt, or in another Companion's wording): expect about 10% of the 111 "clearly left out of Mishkat" to be present after all.
- Rule R1 was right about 9 times in 10 on the samples read; R3 about 11 of 15; R2 about 4 in 10 (so it only creates UNRES).
- The Arabic was read by the assistant; no second independent reviewer checked it.
- Counts of "sahih" are lower bounds for hadith whose grade rests on the Sahihayn inference alone; the 160 with no evidence are not in the sahih count.
