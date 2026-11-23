"""Arabic normalisation helpers shared by all scripts."""
import re
import unicodedata

# harakat, small marks, tatweel, quranic annotation marks
_DIAC = re.compile(r"[ً-ٰٟـۖ-ۭ࣓-ࣿؐ-ؚ]")
_ZW = re.compile(r"[​-‏‪-‮⁦-⁩﻿]")
_NONLETTER = re.compile(r"[^ء-غف-ي\s]")
_WS = re.compile(r"\s+")

# honorific / blessing formulas that differ between editors by spelling only
_FORMULA = [
    (re.compile(r"\bصلي الله عليه وعلي اله وسلم\b"), "صلي الله عليه وسلم"),
    (re.compile(r"\bصلي الله عليه واله وسلم\b"), "صلي الله عليه وسلم"),
]


def strip_diacritics(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = _ZW.sub("", s)
    return _DIAC.sub("", s)


def norm_orth(s: str) -> str:
    """Tier A: remove diacritics/punctuation/digits; keep letter shapes as typed."""
    s = strip_diacritics(s)
    s = _NONLETTER.sub(" ", s)
    return _WS.sub(" ", s).strip()


def norm_loose(s: str) -> str:
    """Tier B: also unify alef/hamza/ya/ta-marbuta spellings."""
    s = strip_diacritics(s)
    s = re.sub("[إأآٱ]", "ا", s)
    s = s.replace("ى", "ي").replace("ئ", "ي").replace("ؤ", "و").replace("ء", "")
    s = s.replace("ة", "ه")
    s = _NONLETTER.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s


def norm_formula(s: str) -> str:
    """Tier C: loose + unify blessing/honorific formula variants."""
    s = norm_loose(s)
    for pat, rep in _FORMULA:
        s = pat.sub(rep, s)
    return s


def tokens(s: str):
    return s.split()
