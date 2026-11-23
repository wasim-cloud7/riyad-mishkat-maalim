#!/usr/bin/env python3
"""Convert Shamela-style HTML exports into page-delimited plain text.

Output format per page:
=====PAGE <n or ?> | seq <k>=====
<body text, paragraphs separated by newlines>
-----FOOTNOTES-----
<footnote text>

Usage: python3 -I html2txt.py <in.htm> <out.txt>
"""
import html
import re
import sys

ZW = dict.fromkeys(map(ord, "‌‍‎‏‪‫‬‭‮﻿"), None)


def convert(path_in, path_out):
    with open(path_in, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    # split into PageText blocks
    parts = re.split(r"<div class='PageText'>", raw)
    out = []
    seq = 0
    for part in parts[1:]:
        seq += 1
        m = re.search(r"\(ص:\s*([0-9٠-٩]+)\)", part)
        pageno = m.group(1) if m else "?"
        # remove page head
        body = re.sub(r"<div class='PageHead'>.*?</div>", "", part, count=1, flags=re.S)
        # separate footnotes
        if "<hr width='95' align='right'>" in body:
            main, foot = body.split("<hr width='95' align='right'>", 1)
        else:
            main, foot = body, ""

        def clean(s):
            s = re.sub(r"<br\s*/?>", "\n", s)
            s = re.sub(r"</p>", "\n", s)
            s = re.sub(r"<p[^>]*>", "\n", s)
            s = re.sub(r"<[^>]+>", "", s)
            s = html.unescape(s)
            s = s.translate(ZW)
            s = s.replace("\xa0", " ")
            lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.split("\n")]
            return "\n".join(ln for ln in lines if ln != "")

        out.append(f"=====PAGE {pageno} | seq {seq}=====")
        out.append(clean(main))
        c = clean(foot)
        if c:
            out.append("-----FOOTNOTES-----")
            out.append(c)
    with open(path_out, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"{path_in}: {seq} page blocks -> {path_out}")


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
