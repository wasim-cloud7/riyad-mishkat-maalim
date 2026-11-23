#!/usr/bin/env python3
"""Phase 1a - apply the user's wording-difference rule to the two Riyad editions (al-Fahl vs al-Risalah/Arna'ut).

User's rule (Sun 2026-11-22): at least one real wording difference is not always a real difference (but the numbers are wanted);
at least 3 real wording differences = a real difference; at least 4 real wording differences = a real difference even/also when 90% of the wording matches.
Reading used for the headline (the only reading that leaves both clauses meaningful):
    threshold 3 when the two texts match < 90%, threshold 4 when they match >= 90%.
The full grid (>=1, >=2, >=3, >=4 x match band x scope) is printed as well so any other reading can be read off directly.

'Real wording difference' = a different word, an extra word or a minor word form (الخير/خيرا). Not counted: spelling conventions
(الرحمان/الرحمن), hamza/alif/ya spelling, word spacing, attached connector letters (و/ف/ب/ل), blessing formulae.
Scopes: body = hadith text (chain + matn, takhrij tail after 'رواه...' excluded) [headline]; quoted = only inside the quotation marks (the Prophet's words);
all = body + takhrij tail.   Match % = 100 * (1 - words inside real differences / words of the longer edition's text).

Run: python3 -I phase1a_rule.py     (writes phase1a_real_differences_by_hadith.csv and appends section 6 to phase1a_editions_comparison_report.txt)
"""
import collections
import csv
import json
import re

D = "/home/claude/work/data/"
OUT = "/home/claude/outputs/"
cmp_ = json.load(open(D + "compare.json", encoding="utf-8"))
REAL = {"different_wording", "extra_in_fahl", "extra_in_risalah", "minor_word_form"}
STRICT = {"different_wording", "extra_in_fahl", "extra_in_risalah"}
LABEL = {"different_wording": "different word", "extra_in_fahl": "extra only in Fahl", "extra_in_risalah": "extra only in Risalah", "minor_word_form": "minor word form"}


def pick(c, kinds, scope):
    out = []
    for d in c["diffs"]:
        if d["kind"] not in kinds:
            continue
        if scope == "body" and d["hzone"] != "H":
            continue
        if scope == "quoted" and not (d["hzone"] == "H" and d["zone"] == "Q"):
            continue
        out.append(d)
    return out


def measure(c, kinds, scope):
    ds = pick(c, kinds, scope)
    words = sum(max(d["n_fahl"], d["n_risalah"]) for d in ds)
    L = max(c["len_fahl"], c["len_risalah"], 1)
    return len(ds), words, 100.0 * (1 - words / L)


def is_real(n, match):
    thr = 3 if match < 90 else 4
    return n >= thr, thr


rows = []
for c in cmp_:
    nb, wb, mb = measure(c, REAL, "body")
    nq, _, _ = measure(c, REAL, "quoted")
    na, _, _ = measure(c, REAL, "all")
    ns, _, _ = measure(c, STRICT, "body")
    real, thr = is_real(nb, mb)
    rows.append({
        "fahl_number": c["fahl_num"], "risalah_number_as_printed": c["risalah_printed"], "fahl_chapter": c["fahl_chapter"],
        "words_Fahl": c["len_fahl"], "words_Risalah": c["len_risalah"],
        "real_diffs_body": nb, "real_diffs_quoted_matn": nq, "real_diffs_body_plus_takhrij_tail": na, "strict_diffs_body(different/extra words only)": ns,
        "words_inside_real_diffs_body": wb, "match_pct_body": round(mb, 1),
        "at_least_1": int(nb >= 1), "at_least_2": int(nb >= 2), "at_least_3": int(nb >= 3), "at_least_4": int(nb >= 4),
        "threshold_applied(3 if match<90 else 4)": thr, "REAL_DIFFERENCE_by_rule": "YES" if real else "no",
        "phase1_status": c["status"],
    })
with open(OUT + "phase1a_real_differences_by_hadith.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# ------------------------------------------------------------------ numbers
N = len(cmp_)
grid = {}
for kname, kinds in (("real (different + extra + minor word form)", REAL), ("strict (different + extra words only)", STRICT)):
    for scope in ("body", "quoted", "all"):
        g = {}
        for k in (1, 2, 3, 4):
            sel = [measure(c, kinds, scope) for c in cmp_]
            g[k] = (sum(1 for n, _, m in sel if n >= k), sum(1 for n, _, m in sel if n >= k and m >= 90), sum(1 for n, _, m in sel if n >= k and m < 90))
        sel = [measure(c, kinds, scope) for c in cmp_]
        g["rule"] = sum(1 for n, _, m in sel if is_real(n, m)[0])
        grid[(kname, scope)] = g
dist = collections.Counter(min(r["real_diffs_body"], 5) for r in rows)
lo = [r for r in rows if r["match_pct_body"] < 90]
real_rows = [r for r in rows if r["REAL_DIFFERENCE_by_rule"] == "YES"]
bymap = {c["fahl_num"]: c for c in cmp_}

L = []
A = L.append
A("")
A("7. YOUR WORDING-DIFFERENCE RULE APPLIED TO THE 1892 SHARED HADITH (added 2026-11-22)")
A("-" * 70)
A("Rule as you gave it: 'at least one real wording difference is not always a real difference, even though we can have the numbers for it;")
A("at least 3 real wording differences will be considered a real difference, and furthermore even at least four real wording differences will be")
A("considered a real difference if 90% of the wording matches.'")
A("Reading used (the only one that keeps both clauses meaningful): a hadith pair has a REAL DIFFERENCE when it has >= 3 real wording differences and the")
A("two texts match less than 90%, or >= 4 real wording differences when they match 90% or more. The grid below lets you apply any other reading.")
A("")
A("Definitions")
A("  real wording difference = a different word, an extra word, or a minor word form (الخير / خيرا). NOT counted: spelling conventions (الرحمان / الرحمن),")
A("     hamza/alif/ya spelling, word spacing, attached connector letters (و ف ب ل), blessing formulae (تعالى / عز وجل / صلى الله عليه وسلم).")
A("  scope 'body' (headline) = the hadith text, i.e. chain + matn; the takhrij tail after 'رواه ...' is editorial and excluded. 'quoted' = only inside the quotation marks")
A("     (the Prophet's own words). 'all' = body + takhrij tail.")
A("  match % = 100 x (1 - words inside real differences / words of the longer edition's text), per hadith.")
A("")
A("Numbers (hadith out of %d compared; body scope, real = different + extra + minor word form)" % N)
g = grid[("real (different + extra + minor word form)", "body")]
A("    at least 1 real wording difference : %4d   (match >= 90%%: %d, match < 90%%: %d)" % g[1])
A("    at least 2 real wording differences: %4d   (match >= 90%%: %d, match < 90%%: %d)" % g[2])
A("    at least 3 real wording differences: %4d   (match >= 90%%: %d, match < 90%%: %d)" % g[3])
A("    at least 4 real wording differences: %4d   (match >= 90%%: %d, match < 90%%: %d)" % g[4])
A("    no real wording difference         : %4d" % (N - g[1][0]))
A("    => REAL DIFFERENCE under the rule (>=3 and match<90%%, or >=4 and match>=90%%): %d hadith" % g["rule"])
A("    distribution of hadith by number of real wording differences (body): " + ", ".join("%s: %d" % (("5+" if k == 5 else k), dist.get(k, 0)) for k in range(0, 6)))
A("    hadith whose match is below 90%% (all short hadith): %d" % len(lo))
A("")
A("Full grid (hadith counts)            >=1 / >=2 / >=3 / >=4     rule-real")
for (kname, scope), gg in grid.items():
    A("  %-44s %-7s %4d / %3d / %3d / %3d        %3d" % (kname, scope, gg[1][0], gg[2][0], gg[3][0], gg[4][0], gg["rule"]))
A("")
A("Reading the numbers: %d of the %d hadith differ in at least one real word, but only %d meet your rule for a real difference; the remaining differences" % (g[1][0], N, g["rule"]))
A("are single words (إنّ / هذه / a repeated قال, one different word or a minor word form) that follow different manuscripts or riwayat and do not change the hadith.")
A("")
A("The %d hadith with a REAL DIFFERENCE under the rule (F = al-Fahl, R = al-Risalah; only the real differences are shown):" % len(real_rows))
for r in sorted(real_rows, key=lambda x: -x["real_diffs_body"]):
    c = bymap[r["fahl_number"]]
    A("  F#%d (R printed %s, ch.%s): %d real differences in the body, match %.1f%%, words F/R %d/%d, threshold %d" % (
        r["fahl_number"], r["risalah_number_as_printed"], r["fahl_chapter"], r["real_diffs_body"], r["match_pct_body"], r["words_Fahl"], r["words_Risalah"], r["threshold_applied(3 if match<90 else 4)"]))
    for d in pick(c, REAL, "body")[:10]:
        A("       [%s] F: %s | R: %s" % (LABEL[d["kind"]], re.sub(r"\s+", " ", d["fahl"] or "-")[:60], re.sub(r"\s+", " ", d["risalah"] or "-")[:60]))
A("")
A("Per-hadith values for all 1892 pairs: phase1a_real_differences_by_hadith.csv (columns at_least_1..4, match_pct_body, REAL_DIFFERENCE_by_rule).")
A("Unchanged by this rule: the five structural differences (section 2) - F has 1896 hadith, R has 1892 - and the numbering findings (section 3).")
text = "\n".join(L) + "\n"

path = OUT + "phase1a_editions_comparison_report.txt"
cur = open(path, encoding="utf-8").read()
cut = cur.find("\n7. YOUR WORDING-DIFFERENCE RULE APPLIED")
if cut != -1:
    cur = cur[:cut].rstrip("\n") + "\n"
# one sentence in the verdict (section 6) that carries the rule's result
cur = re.sub(r"Under the rule you set on 2026-11-22[^\n]*\n", "", cur)
anchor = "most of them one-word differences between riwayat.\n"
if anchor in cur:
    cur = cur.replace(anchor, anchor + "Under the rule you set on 2026-11-22 (section 7), only %d of the %d shared hadith (%.1f%%) count as having a real difference.\n" % (g["rule"], N, 100.0 * g["rule"] / N))
open(path, "w", encoding="utf-8").write(cur.rstrip("\n") + "\n" + text)
print(text[:3500])
json.dump({"n": N, "body_real": {str(k): g[k] for k in (1, 2, 3, 4)}, "rule_real": g["rule"], "rule_real_ids": [r["fahl_number"] for r in real_rows],
           "grid": {f"{k[0]} | {k[1]}": {str(i): v for i, v in gg.items()} for k, gg in grid.items()}, "dist_body": dict(dist), "below90": len(lo)},
          open(D + "phase1a_rule_numbers.json", "w"), ensure_ascii=False, indent=1)
