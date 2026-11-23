#!/usr/bin/env python3
"""Parse the two Riyad as-Saliheen editions (Risalah/Arna'ut and al-Fahl) into
chapter + hadith records and dump JSON.

Run:  python3 -I riyad_parse.py
Outputs: /home/claude/work/data/riyad_risalah.json, riyad_fahl.json, parse_log.json
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnorm import strip_diacritics  # noqa: E402

T = "/home/claude/work/txt/"
OUT = "/home/claude/work/data/"
os.makedirs(OUT, exist_ok=True)

AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

CHAP_RE = re.compile(r"^\s*(\d{1,3})\s*[-–ـ]?\s*(با[بَُ]|بَاب|بَابُ|بابُ|بيان وجوب)")


BOOK_RE = re.compile(r"^(\(\d{1,2}\)\s*[-–ـ]\s*)?كتاب\b")
BOOK_TITLES_NORM = set()  # filled with normalised Fahl book titles for matching unnumbered headings


def is_book_heading(s):
    """True for 'Book' (kitab) divider lines such as '(12) - كتَابُ العِلم' or 'كتابُ العِلم'."""
    from arnorm import norm_loose
    t = norm_loose(s)
    if len(t) > 140:
        return False
    if not BOOK_RE.match(strip_diacritics(s).strip()):
        return False
    # numbered form is always a heading; unnumbered form must look like a known book title
    if re.match(r"^\(\d{1,2}\)", s.strip()):
        return True
    if not BOOK_TITLES_NORM:
        return len(t) < 60
    return any((t.startswith(x) and len(t) <= len(x) + 25) or (x.startswith(t) and len(t) >= 10) for x in BOOK_TITLES_NORM)


def read_blocks(path):
    """Yield (seq, page, line, in_footnote) for each text line."""
    seq = 0
    page = "?"
    in_foot = False
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            m = re.match(r"^=====PAGE (\S+) \| seq (\d+)=====$", line)
            if m:
                page, seq = m.group(1), int(m.group(2))
                in_foot = False
                continue
            if line == "-----FOOTNOTES-----":
                in_foot = True
                continue
            yield seq, page, line, in_foot


def split_footnotes(foot_lines):
    """Group footnote lines into numbered entries; continuation lines are appended."""
    notes = {}
    last = 0
    for ln in foot_lines:
        m = re.match(r"^\((\d{1,3})\)\s*(.*)$", ln)
        if m and int(m.group(1)) == last + 1:
            last = int(m.group(1))
            notes[last] = m.group(2)
        elif last:
            notes[last] += " " + ln
        else:
            notes.setdefault(0, "")
            notes[0] += ln + " "
    return notes


# ------------------------------------------------------------------ Fahl
def parse_fahl():
    log = {"edition": "fahl", "warnings": []}
    chapters = {}  # num -> dict(title, line_idx)
    hadiths = []
    cur_chapter = 0
    chap_counter = 0
    log["chapter_number_typos"] = []
    expected = 1
    cur = None
    page_foot = {}  # seq -> list of lines
    rows = list(read_blocks(T + "riyad_fahl.txt"))
    # collect footnote lines per seq first
    for seq, page, line, in_foot in rows:
        if in_foot and line:
            page_foot.setdefault(seq, []).append(line)
    foot_by_seq = {s: split_footnotes(v) for s, v in page_foot.items()}

    for seq, page, line, in_foot in rows:
        if in_foot:
            continue
        s = line.strip()
        if not s:
            continue
        if is_book_heading(s):
            from arnorm import norm_loose
            BOOK_TITLES_NORM.add(norm_loose(re.sub(r"\(\d+\)\s*$", "", re.sub(r"^\(\d{1,2}\)\s*[-–ـ]\s*", "", s))))
            cur = None
            continue
        m = re.match(r"^(\d{1,4})\s*[-–ـ]\s*(.*)$", s)
        if m:
            num, rest = int(m.group(1)), m.group(2)
            if CHAP_RE.match(s):
                # chapter heading: numbered by running count; printed number kept for audit
                chap_counter += 1
                chapters[chap_counter] = {"num": chap_counter, "printed": num, "title": rest, "seq": seq}
                if num != chap_counter:
                    log["chapter_number_typos"].append({"true": chap_counter, "printed": num})
                cur_chapter = chap_counter
                cur = None
                continue
            if num == expected:
                cur = {
                    "num": num,
                    "chapter": cur_chapter,
                    "seq": seq,
                    "header": s[:80],
                    "lines": [rest],
                    "markers": [],
                    "foot_seqs": set(),
                }
                hadiths.append(cur)
                expected += 1
                continue
        if cur is not None:
            cur["lines"].append(s)
        # chapter intro lines (before first hadith) are ignored for hadith text
    # attach footnotes
    for h in hadiths:
        txt = " ".join(h["lines"])
        marks = [int(x) for x in re.findall(r"\((\d{1,3})\)", txt)]
        h["markers"] = marks
        # footnote lookup by seq of start and following seqs
    # footnote association: scan again, line by line with seq
    cur = None
    hmap = {h["num"]: h for h in hadiths}
    expected = 1
    notes_for = {h["num"]: [] for h in hadiths}
    for seq, page, line, in_foot in rows:
        if in_foot:
            continue
        s = line.strip()
        if not s:
            continue
        if is_book_heading(s):
            cur = None
            continue
        m = re.match(r"^(\d{1,4})\s*[-–ـ]\s*(.*)$", s)
        if m and not CHAP_RE.match(s) and int(m.group(1)) == expected:
            cur = int(m.group(1))
            expected += 1
            line_txt = m.group(2)
        elif m and CHAP_RE.match(s):
            cur = None
            continue
        else:
            line_txt = s
        if cur is not None:
            for mk in re.findall(r"\((\d{1,3})\)", line_txt):
                fn = foot_by_seq.get(seq, {}).get(int(mk))
                if fn:
                    notes_for[cur].append(fn)
    out = []
    for h in hadiths:
        raw = " ".join(h["lines"])
        out.append(
            {
                "num": h["num"],
                "chapter": h["chapter"],
                "seq": h["seq"],
                "raw": raw,
                "footnotes": notes_for[h["num"]],
            }
        )
    log["chapters_found"] = len(chapters)
    log["hadiths_found"] = len(out)
    log["last_hadith_num"] = out[-1]["num"] if out else None
    return {"chapters": chapters, "hadiths": out}, log


# --------------------------------------------------------------- Risalah
HDR_PREFIX = re.compile(r"^\s*([0-9٠-٩][0-9٠-٩\s/\-–ـً-ٟ]*)")


def risalah_header(s):
    """Return (printed_global, local_idx or None, rest_of_line) if the line is a hadith header."""
    s0 = s.strip()
    # chapter heading? (number then باب)
    if CHAP_RE.match(s0):
        return None
    # find prefix consisting of digits and separators up to first Arabic letter
    m = re.match(r"^([0-9٠-٩\s/\-–ـً-ٟ]{1,24})(?=[^\d\s/\-–ـً-ٟ])", s0)
    if not m:
        return None
    prefix = m.group(1)
    groups = re.findall(r"[0-9٠-٩]+", prefix)
    if not groups:
        return None
    # must contain a '/' (n/N form) or end with a dash after a single number followed by 'و' or 'ع'
    rest = s0[m.end():]
    has_slash = "/" in prefix
    nums = [int(g.translate(AR_DIGITS)) for g in groups]
    if has_slash:
        if len(nums) == 1:
            return None
        local, glob = min(nums[:2]), max(nums[:2])
        # '416-5/' -> reversed order but max/min handles
        return glob, local, rest
    # no slash: accept only "N-" followed by Arabic text starting with و / ع / ا / etc., N>=100
    if len(nums) == 1 and re.search(r"[-–ـ]", prefix):
        n = nums[0]
        if n >= 100 and re.match(r"^\s*[وعأاِ]", strip_diacritics(rest)):
            return n, None, rest
    # forms like "13/1892 وعن" already handled by has_slash
    return None


def parse_risalah(fahl_titles=None):
    from arnorm import norm_loose
    log = {"edition": "risalah", "warnings": [], "typo_repairs": [], "chapter_repairs": []}
    rows = list(read_blocks(T + "riyad_risalah.txt"))
    # pre-pass: which chapter numbers have a numbered heading?
    numbered = set()
    for seq, page, line, in_foot in rows:
        s0 = line.strip()
        m0 = CHAP_RE.match(s0) if s0 else None
        if m0 and int(m0.group(1)) <= 372 and "/" not in s0[:12] and not in_foot:
            numbered.add(int(m0.group(1)))
    missing_nums = [n for n in range(1, 373) if n not in numbered]
    title_to_missing = {}
    if fahl_titles:
        for n in missing_nums:
            t = fahl_titles.get(n)
            if t:
                title_to_missing[norm_loose(t)] = n
    # 1. split rows into chapter blocks in document order
    blocks = []  # list of dict(num, title, lines=[(seq,page,line)])
    cur = None
    skip_rest = False  # after a Book heading, ignore its intro until the next chapter heading
    for seq, page, line, in_foot in rows:
        if in_foot:
            continue
        s = line.strip()
        if not s:
            continue
        # unnumbered heading whose title equals the title of a chapter that has no numbered heading
        if title_to_missing and s.startswith("باب") and norm_loose(s) in title_to_missing:
            n_fix = title_to_missing.pop(norm_loose(s))
            cur = {"num": n_fix, "title": s, "seq": seq, "lines": []}
            blocks.append(cur)
            skip_rest = False
            log["chapter_repairs"].append({"chapter": n_fix, "reason": "unnumbered heading matched to Fahl title", "line": s[:80]})
            continue
        m = CHAP_RE.match(s)
        if m and int(m.group(1)) <= 372:
            num = int(m.group(1))
            # chapter heading line must be short-ish (titles) and not a hadith header with '/'
            if "/" not in s[:12]:
                title = re.sub(r"^\s*\d+\s*[-–ـ]?\s*", "", s)
                cur = {"num": num, "title": title, "seq": seq, "lines": []}
                blocks.append(cur)
                skip_rest = False
                continue
        if is_book_heading(s):
            log.setdefault("book_headings_skipped", []).append(s[:60])
            skip_rest = True
            continue
        if cur is not None and not skip_rest:
            cur["lines"].append((seq, page, s))
    log["chapter_blocks_in_doc_order"] = [b["num"] for b in blocks]
    chap_nums = [b["num"] for b in blocks]
    dup = sorted({n for n in chap_nums if chap_nums.count(n) > 1})
    if dup:
        log["warnings"].append(f"duplicate chapter numbers: {dup}")
    missing = [n for n in range(1, 373) if n not in chap_nums]
    if missing:
        log["warnings"].append(f"missing chapter numbers: {missing}")
    # doc order of chapters (detect scrambling)
    doc_order_breaks = [(chap_nums[i - 1], chap_nums[i]) for i in range(1, len(chap_nums)) if chap_nums[i] != chap_nums[i - 1] + 1]
    log["chapter_order_breaks"] = doc_order_breaks

    # 2. within each block, split hadiths
    chapters = {}
    all_h = []
    for b in sorted(blocks, key=lambda x: x["num"]):
        hs = []
        curh = None
        for seq, page, s in b["lines"]:
            hdr = risalah_header(s)
            if hdr:
                glob, local, rest = hdr
                curh = {
                    "printed_global": glob,
                    "printed_local": local,
                    "chapter": b["num"],
                    "seq": seq,
                    "page": page,
                    "lines": [rest],
                }
                hs.append(curh)
            elif curh is not None:
                curh["lines"].append(s)
        chapters[b["num"]] = {"num": b["num"], "title": b["title"], "seq": b["seq"], "n_hadith": len(hs)}
        all_h.extend(hs)
    # 3. true numbering: cumulative over chapters in numeric order
    out = []
    for i, h in enumerate(all_h, start=1):
        out.append(
            {
                "num": i,
                "printed_global": h["printed_global"],
                "printed_local": h["printed_local"],
                "chapter": h["chapter"],
                "seq": h["seq"],
                "page": h["page"],
                "raw": " ".join(h["lines"]),
            }
        )
        if h["printed_global"] != i:
            log["typo_repairs"].append({"true": i, "printed": h["printed_global"], "chapter": h["chapter"]})
    log["chapters_found"] = len(chapters)
    log["hadiths_found"] = len(out)
    return {"chapters": chapters, "hadiths": out}, log


if __name__ == "__main__":
    fahl, flog = parse_fahl()
    ris, rlog = parse_risalah({int(k): v["title"] for k, v in fahl["chapters"].items()})
    json.dump(fahl, open(OUT + "riyad_fahl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(ris, open(OUT + "riyad_risalah.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"fahl": flog, "risalah": rlog}, open(OUT + "parse_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("FAHL   :", flog["chapters_found"], "chapters,", flog["hadiths_found"], "hadiths, last num", flog["last_hadith_num"], flog["warnings"], "chapter-number typos:", flog["chapter_number_typos"])
    print("Risalah chapter repairs:", rlog["chapter_repairs"])
    print("RISALAH:", rlog["chapters_found"], "chapters,", rlog["hadiths_found"], "hadiths", rlog["warnings"])
    print("Risalah chapter order breaks:", rlog["chapter_order_breaks"])
    print("Risalah typo repairs:", len(rlog["typo_repairs"]))
    for t in rlog["typo_repairs"][:60]:
        print("  ", t)
