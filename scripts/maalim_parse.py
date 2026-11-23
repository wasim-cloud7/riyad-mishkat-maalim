#!/usr/bin/env python3
"""Parse maalim.txt (numbered entries 'N.  M - (flags) text [refs]' followed by an optional grade line) into
/home/claude/work/data/maalim.json

N = running number of every block in the file, M = the book's own number (hadith) or chapter number (headings).
Run: python3 -I maalim_parse.py
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnorm import strip_diacritics  # noqa: E402

D = "/home/claude/work/data/"
raw = open("/home/claude/work/txt/maalim.txt", encoding="utf-8").read()
# Arabic-Indic digits -> ascii (references like [خ ٣٩٢٤])
trans = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# the running number N is consecutive 1..max: scan for each expected N in order (robust to header variants)
last_n = 0
mx = max(int(x) for x in re.findall(r"(?m)^(\d+)\.\s", raw))
pos = 0
starts = []
for n in range(1, mx + 1):
    m = re.compile(r"(?m)^%d\.\s+" % n).search(raw, pos)
    if not m:
        print("WARNING: block", n, "not found")
        continue
    starts.append((n, m.start(), m.end()))
    pos = m.end()

class _M:  # tiny adapter so the code below can stay close to a regex-match interface
    def __init__(self, n, bookno, first, start, end):
        self.n, self.bookno, self.first, self._s, self._e = n, bookno, first, start, end
    def start(self): return self._s
    def end(self): return self._e

matches = []
for i, (n, st, en) in enumerate(starts):
    line_end = raw.find("\n", en)
    line_end = len(raw) if line_end < 0 else line_end
    rest = raw[en:line_end]
    mm = re.match(r"^(\d+)\s*-\s*(.*)$", rest)
    if mm:
        bookno, first = int(mm.group(1)), mm.group(2)
    else:
        bookno, first = None, rest
    matches.append(_M(n, bookno, first, st, line_end))
print("block headers:", len(matches))

HEADING_RE = re.compile(r"^(?:\(\w+\)\s*)?(?:كتاب|باب|فصل|الفصل|سورة|الباب|أبواب|بَاب|كِتَاب)\b")
FLAG_RE = re.compile(r"^\(([^)]{1,8})\)\s*")
REF_RE = re.compile(r"\[([^\[\]]*?\d[^\[\]]*?)\]")
GRADE_LINE = re.compile(r"^(?:\[?\s*)?(صحيح|حسن|ضعيف|إسناده|قال الذهبي|قال الحاكم|قال الألباني|منكر|موضوع|شاذ|صحيح لغيره|حسن لغيره|صحيح بشواهده|حسن بشواهده)[^\n]{0,120}$")

blocks = []
for i, m in enumerate(matches):
    end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
    body = raw[m.end() : end]
    blocks.append({"seq": m.n, "bookno": m.bookno, "first": m.first, "body": body})

entries = []
chapter = None
for b in blocks:
    first = b["first"].strip()
    plain = re.sub(r"\s+", " ", strip_diacritics(first)).strip()
    if HEADING_RE.match(plain) and "رضي" not in plain[:60] and len(plain) < 160 and "(" not in plain[:3]:
        chapter = first
        entries.append({"seq": b["seq"], "bookno": b["bookno"], "kind": "heading", "text": first, "chapter": first})
        continue
    # hadith block: first line + continuation lines (until the next header, already cut) -> split into paragraphs
    text_all = (first + b["body"]).strip("\n")  # body already starts with the newline that ends the header line
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text_all) if p.strip()]
    flags = None
    m = FLAG_RE.match(paras[0]) if paras else None
    if m:
        flags = m.group(1)
        paras[0] = paras[0][m.end():]
    main = paras[0] if paras else ""
    grades, notes, extra = [], [], []
    for p in paras[1:]:
        pp = strip_diacritics(p).strip()
        if re.match(r"^(صحيح|حسن|ضعيف|منكر|موضوع|شاذ|صحيح لغيره|حسن لغيره|صحيح بشواهده|حسن بشواهده|صحيح لشواهده)[\s\.،:]*$", pp) or re.match(r"^(صحيح|حسن|ضعيف)[^\n]{0,60}\.$", pp):
            grades.append(pp)
        elif pp.startswith("قال") and len(pp) < 200:
            notes.append(p)
        elif pp.startswith("[وانظر") or pp.startswith("وانظر") or pp.startswith("[انظر"):
            notes.append(p)
        else:
            extra.append(p)
    # all bracket references anywhere in the block
    alltext = "\n".join(paras).translate(trans)
    refs = [r.strip() for r in REF_RE.findall(alltext)]
    entries.append({
        "seq": b["seq"], "bookno": b["bookno"], "kind": "hadith", "flags": flags, "main": main,
        "extra": extra, "grades": grades, "notes": notes, "refs": refs,
        "text": "\n".join([main] + extra), "chapter": chapter,
    })

H = [e for e in entries if e["kind"] == "hadith"]
Hd = [e for e in entries if e["kind"] == "heading"]
json.dump(entries, open(D + "maalim.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("headings:", len(Hd), "hadith blocks:", len(H))
print("first/last seq:", entries[0]["seq"], entries[-1]["seq"], " bookno range of hadith:", min(e["bookno"] for e in H if e["bookno"]), max(e["bookno"] for e in H if e["bookno"]), " hadith without book number:", sum(1 for e in H if not e["bookno"]))
print("flags:", collections.Counter(e["flags"] for e in H).most_common(12))
gc = collections.Counter(("; ".join(e["grades"]) if e["grades"] else "-") for e in H)
print("grade lines:", gc.most_common(14))
print("with refs:", sum(1 for e in H if e["refs"]), " empty text:", sum(1 for e in H if len(e["main"]) < 10))
ln = sorted(len(e["text"]) for e in H)
print("text length min/median/max:", ln[0], ln[len(ln) // 2], ln[-1])
dups = [n for n, c in collections.Counter(e["bookno"] for e in H).items() if c > 1]
print("repeated book numbers:", len(dups), dups[:10])
