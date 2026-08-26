r"""heads, with the openings MEASURED instead of enumerated.

The mirror of `contrib/measured_tails.py` (METHODS method 33), and unbuilt until now
for the same reason the head direction itself was unbuilt until 2026-08-22: attention
went to the end of the name, because that is where the hash keeps a resemblance.

`scripts/tails.py --head` replaces a known name's first k characters with every
k-character string over an alphabet, so each rung costs |alphabet|^k:

    k=3        50,653 beginnings     31.7 B candidates
    k=4     2,085,136 beginnings      3.16 T          ~3.25 hours (heads cannot peel)
    k=5    77,150,032 beginnings     ~117 T           weeks

`contrib/heads_measured_alphabet.py` fixed the *alphabet* of that cross product -- the
head alphabet is not the tail alphabet, and `/` alone heads a third of the corpus. It
did not touch the cross product itself, and the cross product is the expensive half.

Measured tails established the point on the other end of the name: of the 69,343,957
possible 5-character strings, real names only ever end with about 92,000 of them, so an
enumerated pass spends 99.87% of itself asking about strings nothing ends with. The same
is true, harder, at the front: names begin `mc/`, `p9_`, `wpn_`, `vox_`, `i_`, and the
count of distinct k-character openings is far below the count of distinct k-character
endings, because the front of a name is where its directory and its family live.

So this keeps the head method's shape exactly -- cut a known name k characters short at
the FRONT, put a different k-character opening on -- and takes the openings from what
names are observed to begin with.

Two things follow, and both are the point:

  * the enumerated ladder dies at k=4 and this does not. k=6, k=10, k=14 are a minute
    each, and on the tail side yield *rose* with k rather than falling.
  * no alphabet question survives. A measured opening carries `/`, `*`, `[`, `$` and
    anything else real names start with, for free, because it was taken from a real name.

It is deliberately a plan and not a printed list: cutting stems and crossing them with
openings is a cross product, and src/bin/confirm_plan.rs is blunt about never printing
one of those.

    python contrib/measured_heads.py --length 6
    bin\windows\confirm_plan.exe plans/mheads6.txt --size
    bin\windows\confirm_plan.exe plans/mheads6.txt

Note `bare` is deliberately absent. Replacing tails, `bare: yes` supplies the only
opening column and the pass tests nothing without it. Replacing heads the openings ARE
the beginnings, so `bare` would instead add the headless stem alone -- a truncation,
which is a different method. See METHODS.md, "Nobody had ever replaced the front".
"""
import argparse, os, glob, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISHED = ["fnv1a_xmaterials.csv", "fnv1a_ximages.csv",
             "fnv1a_xmodels.csv", "fnv1a_xanims.csv"]
GENERAL = ("image", "material", "xmodel", "xanim")


def load():
    names = set()
    for fn in PUBLISHED:
        p = os.path.join(REPO, "cod-name-db", "csv", fn)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                c = line.find(",")
                if c >= 0:
                    names.add(line[c + 1:])
    for p in glob.glob(os.path.join(REPO, "findings", "*", "*.txt")):
        if os.path.splitext(os.path.basename(p))[0] not in GENERAL:
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                if not line:
                    continue
                c = line.find(",")
                names.add(line[c + 1:] if c >= 0 else line)
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=6,
                    help="how many characters to replace at the front")
    ap.add_argument("--min-opening", type=int, default=1,
                    help="drop openings seen fewer than this many times")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    k = args.length

    names = [n for n in load() if len(n) > k + 3]
    sys.stderr.write("names usable at k=%d: %d\n" % (k, len(names)))

    openings = Counter()
    stems = set()
    for n in names:
        openings[n[:k]] += 1
        stems.add(n[k:])

    keep = [o for o, c in openings.most_common() if c >= args.min_opening]
    stems = sorted(stems)
    sys.stderr.write("distinct %d-character openings observed: %d (keeping %d)\n"
                     % (k, len(openings), len(keep)))

    out = args.out or os.path.join(REPO, "plans", "mheads%d" % k)

    def write(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(r + "\n")

    write(out + ".stems.txt", stems)
    write(out + ".begins.txt", keep)
    rel = os.path.basename(out)
    with open(out + ".txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Written by contrib/measured_heads.py --length %d\n#\n" % k)
        fh.write("# `heads` with the openings measured rather than enumerated: every\n")
        fh.write("# known name cut %d characters short at the FRONT, wearing every\n" % k)
        fh.write("# %d-character opening any name is actually observed to start with.\n\n" % k)
        fh.write("label: measured heads of length %d\n" % k)
        fh.write("begin: @plans/%s.begins.txt\n" % rel)
        fh.write("stem:  @plans/%s.stems.txt\n" % rel)

    total = len(stems) * len(keep)
    enumerated = 38 ** k
    print("k=%d: %s measured openings x %s stems = %s candidates"
          % (k, "{:,}".format(len(keep)), "{:,}".format(len(stems)),
             "{:,}".format(total)))
    print("      enumerated heads would use %s openings -- %.0fx more"
          % ("{:,}".format(enumerated), enumerated / float(len(keep))))
    print("wrote %s.txt" % out)


if __name__ == "__main__":
    main()
