"""Bounded complement of the five-character head alphabet for BO4.

The existing heads-slash plan targets fronts containing a directory separator,
which ordinary tail alphabets cannot spell.  This deliberately samples a small,
stable prefix of that distinct space rather than rerunning the full plan.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
begins = (ROOT / "plans" / "codex_heads5_slash_20260825.begins.txt").read_text(encoding="utf-8").splitlines()
stems = (ROOT / "plans" / "codex_heads5_slash_20260825.stems.txt").read_text(encoding="utf-8").splitlines()
# 1,000 slash-bearing fronts x 5,000 known headless bodies = 5M candidates.
for begin in begins[:1000]:
    for stem in stems[:5000]:
        if begin and stem:
            print(begin + stem)
