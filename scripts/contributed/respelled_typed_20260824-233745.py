"""The respelled Black Ops 1/3 corpora, TYPED by shape, for the typed cross.

Method 18's table lists two external corpora: Black Ops 3's shipped manifests and
the cod-name-db `_v2` tables. Both carry their type explicitly. `borrowed/` holds
two more that do not --

    bo3_respelled.txt   236,821 names
    bo1_respelled.txt     4,686 names

-- older-title names already respelled into this era's spelling by an earlier
session (`t8_`/`t9_` map codes, `mc/` directories). Measured 2026-08-25, almost
none of them are known:

    bo3_respelled   image-shaped 66,572 (66,032 unknown)   material-shaped 63,514 (62,958 unknown)
    bo1_respelled   image-shaped    502 (   502 unknown)   material-shaped  1,410 ( 1,410 unknown)

Method 18 is the finding that *verbatim is the wrong test* -- the `_v2` tables
gave zero verbatim and hundreds typed, because "nothing about the corpus changed,
only whether an image core was asked to wear image decorations". These corpora
have only ever been available verbatim.

**Typed by shape, conservatively.** Only the two shapes this project has actually
measured a convention for are accepted, and the permissive fallback is not:

  * **material** -- begins with one of the measured material directories. That is
    a path, and nothing else in these dumps looks like one.
  * **image** -- ends in a measured channel code (`_c`, `_n`, `_g`, ...), or
    begins `i_`.

A bare underscore name is deliberately NOT typed as `sound_alias` here. That
shape matches binary noise in a strings dump -- the raw `bo3_build.txt` gives
767,311 "aliases" that are mostly hex soup like `0-04090c0j0q0w0_0h0p0y0` -- and
feeding that to a cross would spend the whole pass on garbage.

    python contrib/respelled_typed.py > plans/respelled.manifest.csv
    python scripts/typed_cross.py --source plans/respelled.manifest.csv \
        --write-plans plans/respelled
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAT_DIRS = ("mc/", "wc/", "clt/", "splm/", "vd/", "mcs/", "ei/", "cltp/",
            "vdd/", "el/", "mcp/", "ec/", "mcdp/")
CHANNELS = ("_c", "_n", "_g", "_s", "_m", "_a", "_r", "_o", "_d",
            "_co", "_nml", "_spec", "_gloss", "_mask")
SHAPE = re.compile(r"^[a-z0-9_./$~+-]+$")

SOURCES = ("bo3_respelled.txt", "bo1_respelled.txt")


def classify(s):
    if s.startswith(MAT_DIRS):
        return "material"
    if "/" in s or "\\" in s or "." in s:
        return None
    if s.startswith("i_") or s.endswith(CHANNELS):
        return "image"
    return None


def main():
    out = sys.stdout
    seen = set()
    counts = {"image": 0, "material": 0}
    for src in SOURCES:
        path = os.path.join(REPO, "borrowed", src)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.rstrip("\r\n").strip().lower()
                if not (6 <= len(s) <= 120) or not SHAPE.match(s):
                    continue
                t = classify(s)
                if not t or (t, s) in seen:
                    continue
                seen.add((t, s))
                counts[t] += 1
                out.write(t)
                out.write(",")
                out.write(s)
                out.write("\n")
    sys.stderr.write("respelled_typed: %d image, %d material\n"
                     % (counts["image"], counts["material"]))


if __name__ == "__main__":
    main()
