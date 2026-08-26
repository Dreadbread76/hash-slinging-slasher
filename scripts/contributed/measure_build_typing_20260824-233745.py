"""Can an UNTYPED build dump be typed by shape, so the typed cross can eat it?

Method 18 is the finding that a corpus giving zero verbatim gives hundreds when
each type is asked to wear its own decorations. Its stated limit is the corpus,
not the method:

    ... where `zone/` has every asset in the game but only as strings that have
    to be harvested and carry no type at all.

That strands the two largest corpora on this disk -- `borrowed/bo3_build.txt`
(1,231,311 strings) and `borrowed/bo1_build.txt` (325,956) -- from the one method
measured to work on borrowed material.

But a type does not have to be *declared* to be known. These conventions are
strongly shaped, and this project has already measured them:

  * an **image** carries a channel code -- `_c`, `_n`, `_g`, `_s`, `_m`, ... --
    and often a leading `i_`;
  * a **material** is a path under a known directory (`mc/`, `wc/`, `clt/`, ...)
    and usually an `mtl_` after it;
  * a **sound_asset** is a path with a dotted encoding tail (`.ln100.pc.snd`);
  * a **sound_alias** is the one method 18 found richest, and its shape is the
    most distinctive of all precisely because it is the plainest: a bare
    underscore name, no directory, no dot, no channel code.

So this counts, for each shape, how many strings in a build dump match it and are
NOT already known to us -- which is the number that decides whether typing the
dump is worth building. A shape whose matches are all already named is no use;
the ceiling is the unknown ones.

Read-only: classifies strings, prints counts, writes nothing.
"""
import os, glob, re, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAT_DIRS = ("mc/", "wc/", "clt/", "splm/", "vd/", "mcs/", "ei/", "cltp/",
            "vdd/", "el/", "mcp/", "ec/", "mcdp/")
CHANNELS = ("_c", "_n", "_g", "_s", "_m", "_a", "_r", "_o", "_d",
            "_co", "_nml", "_spec", "_gloss", "_mask")

PRINTABLE = re.compile(r"^[a-z0-9_./\\$~+-]+$")


def load_known():
    known = set()
    for p in glob.glob(os.path.join(REPO, "cod-name-db", "csv", "*.csv")):
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                c = line.find(",")
                if c >= 0:
                    known.add(line[c + 1:].lower())
    for p in glob.glob(os.path.join(REPO, "findings", "*", "*.txt")):
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                if not line:
                    continue
                c = line.find(",")
                known.add((line[c + 1:] if c >= 0 else line).lower())
    return known


def classify(s):
    """The type this string's SHAPE says it is, or None if the shape says nothing."""
    if "." in s and (".snd" in s or re.search(r"\.[a-z]{2}\d+\.", s)):
        return "sound_asset"
    if s.startswith(MAT_DIRS):
        return "material"
    if "/" in s or "\\" in s:
        return None          # a path of some other kind; shape does not say
    if "." in s:
        return None
    if s.startswith("i_") or s.endswith(CHANNELS):
        return "image"
    if "_" in s:
        return "sound_alias"
    return None


def main():
    known = load_known()
    sys.stderr.write("known names loaded: %d\n" % len(known))

    for src in ("bo3_build.txt", "bo1_build.txt", "bo3_respelled.txt",
                "bo1_respelled.txt"):
        path = os.path.join(REPO, "borrowed", src)
        if not os.path.exists(path):
            continue
        total = usable = 0
        shaped, unknown = Counter(), Counter()
        samples = {}
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.rstrip("\r\n").strip().lower()
                total += 1
                if len(s) < 6 or len(s) > 120 or not PRINTABLE.match(s):
                    continue
                usable += 1
                t = classify(s)
                if not t:
                    continue
                shaped[t] += 1
                if s not in known:
                    unknown[t] += 1
                    samples.setdefault(t, []).append(s)
        print()
        print("=== %s === %d lines, %d usable as names" % (src, total, usable))
        print("  %-13s %10s %10s" % ("shape", "matched", "NOT known"))
        for t in ("image", "material", "sound_alias", "sound_asset"):
            print("  %-13s %10d %10d" % (t, shaped[t], unknown[t]))
        for t in ("sound_alias", "image", "material", "sound_asset"):
            ex = samples.get(t, [])[:4]
            if ex:
                print("     %-11s e.g. %s" % (t, ", ".join(ex)))


if __name__ == "__main__":
    main()
