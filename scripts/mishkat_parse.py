#!/usr/bin/env python3
"""Parse the three Mishkat al-Masabih text files (Albani edition, grade label printed in parentheses on the
header line of every hadith) into /home/claude/work/data/mishkat.json

Run: python3 -I mishkat_parse.py
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnorm import strip_diacritics  # noqa: E402

D = "/home/claude/work/data/"
units = []
for k in (1, 2, 3):
    t = open(f"/home/claude/work/txt/mishkat_{k}.txt", encoding="utf-8").read()
    parts = re.split(r"(?m)^=====PAGE (\S+) \| seq (\d+)=====$", t)
    for i in range(1, len(parts), 3):
        units.append({"vol": k, "page": parts[i], "seq": int(parts[i + 1]), "body": parts[i + 2].strip()})

HDR_A = re.compile(r"^(\d+)\s*-\s*(?:\[(\d+)\])?\s*\(([^)]*)\)\s*$")
HDR_B = re.compile(r"^(\d+)\s*-\s*(?:\[(\d+)\])?\s*(.*)$", re.S)
HDR_C = re.compile(r"^(\d+)\s*\(([^)]*)\)?\s*$")  # '42 (لم تتمّ دراسته'
BOOK = re.compile(r"^(?:\[\d+\]\s*)?(كتاب|كِتَاب)\s")
BAB = re.compile(r"^(?:\[\d+\]\s*)?(بَاب|باب|بَابُ)\s")
FASL = re.compile(r"^(الْفَصْل|الْفَصْلُ|الفصل)\s")


def label_family(lbl):
    if lbl is None:
        return "NO_LABEL"
    s = strip_diacritics(lbl)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("لم تتمدراسته", "لم تتم دراسته")
    if "لم تتم" in s:
        return "NOT_STUDIED"
    if s.startswith("متفق") or "متفق عل" in s:
        return "SAHIHAYN"
    if any(w in s for w in ("موضوع", "باطل", "لا اصل", "لا أصل")):
        return "MAWDU"
    if any(w in s for w in ("ضعيف", "واه", "منكر")):
        return "DAIF"
    if "صحيح" in s and "حسن" in s:
        return "HASAN_SAHIH"
    if "صحيح" in s:
        return "SAHIH"
    if "حسن" in s:
        return "HASAN"
    if "جيد" in s:
        return "JAYYID"
    if "موقوف" in s or "مرسل" in s:
        return "MAWQUF_MURSAL"
    return "OTHER"


entries = []
cur = None
book = bab = fasl = None
pending_heading = None  # last heading kind, to absorb continuation lines
for u in units:
    body = u["body"]
    if not body:
        continue
    lines = body.split("\n")
    first = lines[0].strip()
    rest = "\n".join(lines[1:]).strip()
    if u["vol"] == 1 and u["seq"] <= 7:  # preface / title page
        continue
    m = HDR_A.match(first)
    if m:
        num, fn, lbl = int(m.group(1)), m.group(2), m.group(3)
        cur = {"num": num, "fn": fn, "label": re.sub(r"\s+", " ", lbl).strip(), "text": rest, "vol": u["vol"], "page": u["page"],
               "seq": u["seq"], "book": book, "bab": bab, "fasl": fasl, "form": "A"}
        entries.append(cur)
        pending_heading = None
        continue
    m = HDR_C.match(first)
    if m:
        cur = {"num": int(m.group(1)), "fn": None, "label": re.sub(r"\s+", " ", m.group(2)).strip(), "text": rest, "vol": u["vol"], "page": u["page"],
               "seq": u["seq"], "book": book, "bab": bab, "fasl": fasl, "form": "C"}
        entries.append(cur)
        pending_heading = None
        continue
    if re.match(r"^\d+\s*-", first):
        m = HDR_B.match(first)
        num, fn, tail = int(m.group(1)), m.group(2), m.group(3)
        txt = (tail + ("\n" + rest if rest else "")).strip()
        cur = {"num": num, "fn": fn, "label": None, "text": txt, "vol": u["vol"], "page": u["page"], "seq": u["seq"],
               "book": book, "bab": bab, "fasl": fasl, "form": "B"}
        entries.append(cur)
        pending_heading = None
        continue
    # headings
    if BOOK.match(first) and len(first) < 90 and not rest:
        book, bab, fasl = first, None, None
        pending_heading = "book"
        continue
    if BAB.match(first) and len(first) < 160 and not rest:
        bab, fasl = re.sub(r"^\[\d+\]\s*", "", first), None
        pending_heading = "bab"
        continue
    if FASL.match(first) and len(first) < 40 and not rest:
        fasl = first
        pending_heading = "fasl"
        continue
    # continuation of a heading line split over two units, or of a hadith
    if pending_heading in ("bab", "book") and len(first) < 120:
        if pending_heading == "bab":
            bab = (bab or "") + " " + first
        else:
            book = (book or "") + " " + first
        continue
    if cur is not None:
        cur["text"] = (cur["text"] + "\n" + body).strip()
        cur["continued"] = True

# drop numbered lists that are not hadith (e.g. names of the Badr participants) and heading lines that carry a number:
# real hadith numbers increase monotonically through the book
acc, dropped, last = [], [], 0
for e in entries:
    if last < e["num"] <= last + 60:
        acc.append(e)
        last = e["num"]
    else:
        dropped.append(e)
entries = acc

# clean + families
for e in entries:
    e["text"] = re.sub(r"[ \t]+", " ", e["text"]).strip()
    e["family"] = label_family(e["label"])

nums = [e["num"] for e in entries]
dup = [n for n, c in collections.Counter(nums).items() if c > 1]
missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
json.dump(entries, open(D + "mishkat.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("dropped non-hadith units:", [(e["num"], e["vol"], e["seq"], e["text"][:30].replace("\n", " ")) for e in dropped][:12], len(dropped))
print("entries:", len(entries), "max num:", max(nums), "distinct:", len(set(nums)))
print("duplicates:", dup[:20], len(dup))
print("missing numbers:", len(missing), missing[:40])
print("forms:", collections.Counter(e["form"] for e in entries))
print("families:", collections.Counter(e["family"] for e in entries))
print("with continuation:", sum(1 for e in entries if e.get("continued")))
ln = [len(e["text"]) for e in entries]
print("text length: min", min(ln), "median", sorted(ln)[len(ln) // 2], "max", max(ln), "short(<25):", sum(1 for x in ln if x < 25))
print("books:", len({e['book'] for e in entries}), "babs:", len({e['bab'] for e in entries}))
