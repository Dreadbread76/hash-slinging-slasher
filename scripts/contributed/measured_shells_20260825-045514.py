r"""A known name's MIDDLE, wearing a different name's opening and a different name's ending.

    python contrib/measured_shells.py --head 6 --tail 6 --top 1200
    bin\windows\confirm_plan.exe plans/shell_h6t6.txt --size
    bin\windows\confirm_plan.exe plans/shell_h6t6.txt

## Where this comes from

Two methods here cut a known name at a **character offset** and replace one side with a
vocabulary measured off the corpus rather than enumerated from an alphabet:

    measured tails (method 33)   name[:-k] + <observed k-character ending>
    measured heads (method 34)   <observed k-character opening> + name[k:]

Both work, and on both the yield *rises* with k rather than falling. Neither has ever been
combined with the other, and the engine does that natively: `confirm_plan` is a
`begin x stem x end` cross product and these two methods each leave one of the three columns
empty.

## Why it is not the general search under another name

`confirm_cw` is also `begin x core x end`, so the shape is not new -- what is fed to it is.
Its `data/prefixes.txt` and `data/suffixes.txt` are cut at **token boundaries**: they are the
underscore-separated pieces names are built from. That is a different set of strings from the
ones measured here, which are cut at a fixed character count and cheerfully straddle a boundary
(`ial_n`, `s_02_`, `mc/t8_`). The whole finding behind methods 33 and 34 is that the
character-offset cut reaches names the token cut does not -- so doing it on both ends at once
is ground neither the general search nor either method covers.

## Why it needs a cap and how to set it

The measured vocabularies are small for a cross product of two but not of three: at k=6 there
are 5,971 openings and 128,336 endings, which against ~850,000 middles is 6.5e14 candidates.
`--top N` keeps the N commonest of each, so the pass is N x middles x N and the cost is
quadratic in N. Size it before running it -- 1,200 each is about 1.2e12, roughly twenty minutes
on sixteen cores; 400 each is 1.4e11 and a couple of minutes.

Frequency is the right thing to rank by here, unlike in methods 33 and 34 where the whole
vocabulary is affordable and ranking is unnecessary. An opening seen once heads one name; an
opening seen 400,000 times is a directory.
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
    ap.add_argument("--head", type=int, default=6, help="characters replaced at the front")
    ap.add_argument("--tail", type=int, default=6, help="characters replaced at the end")
    ap.add_argument("--top", type=int, default=1200,
                    help="keep the N commonest openings and the N commonest endings")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    h, t = args.head, args.tail

    # A middle has to survive both cuts and still be worth something, so the name must be longer
    # than the two cuts plus a few characters -- otherwise the "middle" is two characters and the
    # candidate is just an opening glued to an ending, which is the splice this file records dead.
    names = [n for n in load() if len(n) > h + t + 4]
    sys.stderr.write("names usable at head=%d tail=%d: %d\n" % (h, t, len(names)))

    openings, endings, middles = Counter(), Counter(), set()
    for n in names:
        openings[n[:h]] += 1
        endings[n[-t:]] += 1
        middles.add(n[h:-t])

    begins = [o for o, _ in openings.most_common(args.top)]
    ends = [e for e, _ in endings.most_common(args.top)]
    middles = sorted(middles)

    out = args.out or os.path.join(REPO, "plans", "shell_h%dt%d" % (h, t))

    def write(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(r + "\n")

    write(out + ".begins.txt", begins)
    write(out + ".mids.txt", middles)
    write(out + ".ends.txt", ends)
    rel = os.path.basename(out)
    with open(out + ".txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Written by contrib/measured_shells.py --head %d --tail %d --top %d\n#\n"
                 % (h, t, args.top))
        fh.write("# Every known name with %d characters cut off the front and %d off the end,\n"
                 % (h, t))
        fh.write("# wearing every opening and every ending the corpus is observed to use at\n")
        fh.write("# those lengths -- the two measured-offset methods applied at once.\n\n")
        fh.write("label: measured shells, head %d tail %d, top %d\n" % (h, t, args.top))
        fh.write("begin: @plans/%s.begins.txt\n" % rel)
        fh.write("stem:  @plans/%s.mids.txt\n" % rel)
        fh.write("end:   @plans/%s.ends.txt\n" % rel)

    total = len(begins) * len(middles) * len(ends)
    print("head=%d tail=%d top=%d: %s openings x %s middles x %s endings = %s candidates"
          % (h, t, args.top, "{:,}".format(len(begins)), "{:,}".format(len(middles)),
             "{:,}".format(len(ends)), "{:,}".format(total)))
    print("      full vocabulary would be %s x %s -- capped %.0fx"
          % ("{:,}".format(len(openings)), "{:,}".format(len(endings)),
             (len(openings) * len(endings)) / float(max(1, len(begins) * len(ends)))))
    print("wrote %s.txt" % out)


if __name__ == "__main__":
    main()
