"""Builds the compact "left out" tables (opening words only) used for the Notion list pages.
Reads outputs/phase2/phase2_master_riyad.csv, writes the four tables next to the script output dir. Run from any directory."""
OUT = "/home/claude/outputs/phase2/compact_tables/"
import csv, sys, re, collections
sys.path.insert(0, "/home/claude/scripts")
from arnorm import strip_diacritics
rows = list(csv.DictReader(open("/home/claude/outputs/phase2/phase2_master_riyad.csv", encoding="utf-8-sig")))
print(len(rows))
print(collections.Counter(r["combined_class"] for r in rows))
print(collections.Counter((r["mishkat_3state"], r["maalim_3state"]) for r in rows if r["combined_class"]=="SAHIH"))
print(collections.Counter(r["in_Bukhari_or_Muslim"] for r in rows))
def snip(t, n=10):
    t = strip_diacritics(t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^[^:]{1,30}:\s*(?=و?عن\s)", "", t)          # ordinal prefix such as 'التاسع:'
    t = re.sub(r"^(و?عن)\s+", "", t)
    t = re.sub(r"رضي الله (عنهما|عنهم|عنهن|عنها|عنه)", "", t)
    t = re.sub(r"صلى الله عليه وسلم", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    w = t.split(" ")
    return " ".join(w[:n]).replace("|", "/")
def table(sel, cols):
    out = ["| " + " | ".join(h for h, _ in cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in sel:
        out.append("| " + " | ".join(f(r) for _, f in cols) + " |")
    return "\n".join(out)
def src(r):
    return r["sources_all"].replace("|", "/") or "-"
cols_both = [("F#", lambda r: r["fahl_no"]), ("Ch.", lambda r: r["chapter_no"]), ("Albani family", lambda r: r["albani_family"]), ("Sources", src), ("Opening words", lambda r: snip(r["text"]))]
S = [r for r in rows if r["combined_class"] == "SAHIH"]
both = [r for r in S if r["mishkat_3state"] == "OUT" and r["maalim_3state"] == "OUT"]
mis = [r for r in S if r["mishkat_3state"] == "OUT"]
mal = [r for r in S if r["maalim_3state"] == "OUT"]
print(len(both), len(mis), len(mal))
cols_mis = cols_both[:4] + [("Ma'alim", lambda r: {"IN":"in","OUT":"out","UNRES":"unresolved"}[r["maalim_3state"]]), cols_both[4]]
cols_mal = cols_both[:4] + [("Mishkat", lambda r: {"IN":"in","OUT":"out","UNRES":"unresolved"}[r["mishkat_3state"]]), cols_both[4]]
open(OUT + "left_out_of_both_57.md", "w", encoding="utf-8").write(table(both, cols_both))
open(OUT + "left_out_of_mishkat_111.md", "w", encoding="utf-8").write(table(mis, cols_mis))
mal_bm = [r for r in mal if r["in_Bukhari_or_Muslim"] == "Y"]
mal_nb = [r for r in mal if r["in_Bukhari_or_Muslim"] != "Y"]
print(len(mal_bm), len(mal_nb))
open(OUT + "left_out_of_maalim_284_cited_to_bukhari_muslim.md", "w", encoding="utf-8").write(table(mal_bm, cols_mal))
open(OUT + "left_out_of_maalim_51_other_books.md", "w", encoding="utf-8").write(table(mal_nb, cols_mal))
