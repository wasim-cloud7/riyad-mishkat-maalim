# Cross-check of the "clearly left out" lists (24 Nov 2026)

Lists checked: the 111 sahih Riyad hadith classed as clearly left out of Mishkat and the 335 classed as clearly left out of Ma'alim
(the 57 left out of both are part of both lists).

Method (`scripts/crosscheck_left_out.py`): for each hadith, take its 8 rarest words (by inverse document frequency) and count how many of them occur in each
Mishkat entry (6,283) and each Ma'alim block (3,373). An entry sharing 5 or more of the 8 is flagged for a human look.
The search only finds hadith that share unusual words. It lowers the chance of a missed counterpart; it cannot prove there is none.

## Result

| book | hadith checked | flagged | real counterpart found |
| --- | --- | --- | --- |
| Mishkat | 111 | 6 | 0 |
| Ma'alim | 335 | 12 | 0 |

Mishkat flags (what each is):

| F# | hadith | nearest Mishkat entry | judgement |
| --- | --- | --- | --- |
| 240 | Abu Hurayra, "no servant conceals another's faults in this world but God conceals his on the Day of Resurrection" (Muslim) | #204, a longer Abu Hurayra hadith that contains "whoever conceals a Muslim" | same theme, different hadith |
| 1634 | Jabir, "do not eat with the left hand" (Muslim) | #4163, Ibn 'Umar's wording of the same rule (Muslim) | different Companion, different narration |
| 762, 916, 1161, 1602 | various | various unrelated entries | chance overlap on common words |

Ma'alim flags (F# 370, 548, 765, 937, 1288, 1334, 1510, 1619, 1682, 1740, 1776, 1813): every flagged block is a long, unrelated narration
(for example the Hudaybiyya or Ka'b ibn Malik stories) that shares common words such as "Allah's Messenger" and "the Day of Judgment". None is a counterpart.

## What it changes

Earlier hand spot-checks had suggested that up to about 10% of the 111 might still have a counterpart. The systematic cross-check found none,
so the 111 and the 335 stand as the clear-cut lower bound. The 140 (Mishkat) and 124 (Ma'alim) hadith kept as "unresolved" are the only ones that could still move into "in".
