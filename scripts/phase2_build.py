#!/usr/bin/env python3
"""Phase 2 master table: every Riyad hadith (al-Fahl numbering 1..1896) with
  - source books (Nawawi + al-Fahl takhrij + matched Mishkat/Ma'alim attributions)
  - grading evidence ladder (Albani / Arna'ut / combined)
  - presence status in Mishkat and in Ma'alim
Writes /home/claude/work/data/phase2_master.pkl  (list of dicts) and prints headline checks.
Run: python3 -I phase2_build.py
"""
import collections
import json
import os
import pickle
import re
import sys

sys.path.insert(0, "/home/claude/scripts")
from arnorm import strip_diacritics  # noqa: E402
import hm_status  # noqa: E402

D = "/home/claude/work/data/"

SAHIH_SET = {"SAHIH", "SAHIH_LIGHAYRIHI", "SAHIHAYN", "SAHIHAYN_INFERRED"}
STRICT_SAHIH = {"SAHIH", "SAHIHAYN", "SAHIHAYN_INFERRED"}
HASAN_SET = {"HASAN", "HASAN_LIGHAYRIHI", "JAYYID", "HASAN_SAHIH"}
DAIF_SET = {"DAIF", "MAWDU"}
OTHER_SET = {"SHADH", "MIXED", "OTHER", "SAHIH_MURSAL"}
RANK = {"SAHIH": 5, "SAHIH_LIGHAYRIHI": 5, "SAHIHAYN": 5, "SAHIHAYN_INFERRED": 5,
        "HASAN": 4, "HASAN_LIGHAYRIHI": 4, "JAYYID": 4, "HASAN_SAHIH": 4,
        "SHADH": 3, "MIXED": 3, "OTHER": 3, "SAHIH_MURSAL": 3, "DAIF": 2, "MAWDU": 1}


def fam_label(lbl):
    """Grade label (as printed) -> family"""
    if not lbl:
        return "NO_LABEL"
    s = re.sub(r"\s+", " ", strip_diacritics(lbl)).strip().replace("لم تتمدراسته", "لم تتم دراسته")
    if "لم تتم" in s:
        return "NOT_STUDIED"
    if s.startswith("متفق") or "متفق عل" in s:
        return "SAHIHAYN"
    if any(w in s for w in ("موضوع", "باطل", "لا اصل", "لا أصل", "لاأصل")):
        return "MAWDU"
    if any(w in s for w in ("ضعيف", "واه", "منكر")):
        return "DAIF"
    if "شاذ" in s and "صحيح" in s:
        return "MIXED"
    if "شاذ" in s:
        return "SHADH"
    if "صحيح" in s and "حسن" in s:
        return "HASAN_SAHIH"
    if "صحيح" in s:
        if "مرسل" in s:
            return "SAHIH_MURSAL"
        if any(w in s for w in ("لغيره", "لشواهد", "بشواهد", "لطرقه", "بما قبله", "بالذي بعده")):
            return "SAHIH_LIGHAYRIHI"
        return "SAHIH"
    if "حسن" in s:
        if any(w in s for w in ("لغيره", "لشاهد", "بشواهد", "بما قبله")):
            return "HASAN_LIGHAYRIHI"
        return "HASAN"
    if "جيد" in s:
        return "JAYYID"
    return "OTHER"


def main():
    c = pickle.load(open(D + "corpora.pkl", "rb"))
    R = {d["id"]: d for d in c["riyad"]}
    srcs = pickle.load(open(D + "sources.pkl", "rb"))
    f = json.load(open(D + "riyad_fahl.json", encoding="utf-8"))
    chap = {int(k): v for k, v in f["chapters"].items()}
    alb = {a["fahl_num"]: a for a in json.load(open(D + "albani.json", encoding="utf-8")) if a["kind"] == "hadith" and a.get("fahl_num")}
    mis = {e["num"]: e for e in json.load(open(D + "mishkat.json", encoding="utf-8"))}
    mal = {e["seq"]: e for e in json.load(open(D + "maalim.json", encoding="utf-8")) if e["kind"] == "hadith"}
    stM = hm_status.all_status("riyad", "mishkat")
    stA = hm_status.all_status("riyad", "maalim")

    SIX = {"B", "M", "D", "T", "N", "J"}
    rows = []
    conflicts = []
    for rid in sorted(R):
        d = R[rid]
        s = srcs[rid]
        # primary evidence (Nawawi's own attribution + al-Fahl's takhrij) decides Bukhari/Muslim and six-book membership;
        # cross-book attributions (matched Mishkat / Ma'alim entry) are only used to detect Ahmad, Muwatta and other books
        up = set(s["nawawi"]) | set(s["fahl"])
        u = up | set(s["mishkat"]) | set(s["maalim"])
        if rid == 1013:  # Bukhari only mu'allaq (taliq) -> not a Sahihayn narration
            up.discard("B")
            u.discard("B")
        u = (u - SIX) | (up & SIX)
        in_bm = bool(up & {"B", "M"})
        in_six = bool(up & SIX)
        naw = set(s["nawawi"])
        if rid == 1013:
            naw.discard("B")
        naw_any = bool(naw)
        # Sahihayn-based inference of "sahih" needs Nawawi's own attribution to Bukhari/Muslim (or Nawawi gives no
        # recognisable attribution at all and al-Fahl's takhrij lists them). If only al-Fahl lists B/M while Nawawi
        # attributes the narration to another book, the narration may differ from the Sahihayn wording -> no inference.
        sahihayn_primary = bool(naw & {"B", "M"}) or (bool(set(s["fahl"]) & {"B", "M"}) and not naw_any)
        bm_takhrij_only = in_bm and not sahihayn_primary
        if in_bm:
            part = "P1_in_Bukhari_or_Muslim"
        elif in_six:
            part = "P2_in_six_not_BM"
        elif "A" in u:
            part = "P3_Ahmad_not_six"
        elif "MAL" in u:
            part = "P4_Muwatta_not_six_not_Ahmad"
        else:
            part = "P5_none_of_six_Ahmad_Muwatta"
        # ---------------- grading ladder
        a = alb.get(rid)
        a_file_fam = fam_label(a["label"]) if a else None
        mst, mtid, mm, msc = stM[rid]
        mlabel = mis[mtid]["label"] if (mtid and mtid in mis and mst == "IN_CONFIRMED") else None
        mfam = fam_label(mlabel) if mlabel is not None or (mtid and mst == "IN_CONFIRMED") else None
        if mtid and mst == "IN_CONFIRMED" and mlabel is None:
            mfam = "NO_LABEL"
        # ladder for Albani
        if a and a_file_fam != "NO_LABEL":
            a_fam, a_rung, a_raw = a_file_fam, "A2_Albani_Riyad_file", a["label"]
        elif mfam and mfam not in ("NOT_STUDIED", "NO_LABEL"):
            a_fam, a_rung, a_raw = mfam, "A3_Albani_Mishkat_label", mlabel
        elif sahihayn_primary:
            a_fam, a_rung, a_raw = "SAHIHAYN_INFERRED", "A1_Sahihayn_inferred", ""
        else:
            a_fam, a_rung, a_raw = "UNGRADED", "A0_no_evidence", ""
        review = ""
        if sahihayn_primary and a_rung in ("A2_Albani_Riyad_file", "A3_Albani_Mishkat_label") and a_fam not in SAHIH_SET:
            conflicts.append((rid, a_rung, a_fam, a_raw))
            review = "Albani explicit non-sahih label vs Sahihayn attribution"
        # Arna'ut: only the Sahihayn inference is available (no footnote data in the supplied Risalah file)
        n_fam, n_rung = ("SAHIHAYN_INFERRED", "N1_Sahihayn_inferred") if sahihayn_primary else ("UNGRADED", "N0_no_data")
        # combined: best (most favourable) family; sahih if either says sahih
        cand = [x for x in (a_fam, n_fam) if x != "UNGRADED"]
        comb = max(cand, key=lambda k: RANK.get(k, 0)) if cand else "UNGRADED"
        ma_entry = mal.get(stA[rid][1]) if stA[rid][1] else None
        rows.append({
            "id": rid, "chapter_no": d["chapter"], "chapter": chap.get(d["chapter"], {}).get("title", ""),
            "text": d["text"], "nawawi_attrib": d["attrib"],
            "src_nawawi": sorted(s["nawawi"]), "src_fahl": sorted(s["fahl"]), "src_mishkat": sorted(s["mishkat"]), "src_maalim": sorted(s["maalim"]),
            "sources": sorted(u), "in_BM": in_bm, "in_six": in_six, "in_Ahmad": "A" in u, "in_Muwatta": "MAL" in u, "partition": part,
            "albani_file_label": a["label"] if a else "", "albani_file_num": a["albani_num"] if a else "",
            "mishkat_label": mlabel or "", "mishkat_label_family": mfam or "",
            "albani_family": a_fam, "albani_rung": a_rung, "albani_label_used": a_raw,
            "arnaut_family": n_fam, "arnaut_rung": n_rung,
            "combined_family": comb, "review_flag": review, "bm_by_takhrij_only": bm_takhrij_only,
            "combined_class": ("SAHIH" if comb in SAHIH_SET else "HASAN" if comb in HASAN_SET else "DAIF" if comb in DAIF_SET else "OTHER" if comb in OTHER_SET else "UNGRADED"),
            "combined_strict_sahih": comb in STRICT_SAHIH,
            "mishkat_status": mst, "mishkat_id": mtid or "", "mishkat_score": msc if msc is not None else "",
            "maalim_status": stA[rid][0], "maalim_id": stA[rid][1] or "", "maalim_score": stA[rid][3] if stA[rid][3] is not None else "",
            "maalim_bookno": (mal[stA[rid][1]]["bookno"] if stA[rid][1] in mal else ""),
            "maalim_grade_lines": " | ".join(ma_entry["grades"]) if ma_entry and stA[rid][0] in ("IN_CONFIRMED", "IN_PROBABLE") else "",
        })
    pickle.dump(rows, open(D + "phase2_master.pkl", "wb"))
    print("rows", len(rows))
    print("partition:", dict(collections.Counter(r["partition"] for r in rows)))
    print("albani rung:", dict(collections.Counter(r["albani_rung"] for r in rows)))
    print("albani family:", dict(collections.Counter(r["albani_family"] for r in rows)))
    print("combined class:", dict(collections.Counter(r["combined_class"] for r in rows)))
    print("conflicts (B/M hadith with explicit non-sahih Albani label):", conflicts)
    print("mishkat status:", dict(collections.Counter(r["mishkat_status"] for r in rows)))
    print("maalim status:", dict(collections.Counter(r["maalim_status"] for r in rows)))


if __name__ == "__main__":
    main()
