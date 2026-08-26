"""Measure the real directory vocabulary of BO4/CW names, against what is carried.

CLAUDE.md records that material names are paths and that there are "twelve
directories, not one" -- mc/ wc/ clt/ splm/ vd/ mcs/ ei/ cltp/ vdd/ el/ mcp/ ec/.
That fact came from the published tables. `reach.py` and `uncarried.py` both now
point at `mcdp/mtl_` as the single commonest beginning no cut of which is carried
(658 published names), and `unnamed_profile.py` puts `mcdp/` at 3,183 names among
the recovered against 0.04% of the published -- i.e. it is a directory this
project keeps *finding* and never *spelling*.

So the twelve may simply be incomplete. This counts every directory head actually
observed, in the published BO4/CW tables and in everything this project has
confirmed, and says which ones `data/prefixes.txt` cannot express.

Read-only. Prints a table; writes nothing.
"""
import os, sys, glob
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# BO4/BOCW tables only. The _v2 tables are MWII/MWIII/BO6/BO7/WZM under the IW
# offset -- different games, and hashing their names here is measured dead
# (METHODS.md, "Names published for the newer titles").
PUBLISHED = [
    "fnv1a_xmaterials.csv", "fnv1a_ximages.csv",
    "fnv1a_xmodels.csv", "fnv1a_xanims.csv",
]


def names_from_csv(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            comma = line.find(",")
            if comma < 0:
                continue
            yield line[comma + 1:]


def names_from_findings(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            comma = line.find(",")
            yield line[comma + 1:] if comma >= 0 else line


def head_of(name):
    """The directory head: everything up to and including the first slash."""
    slash = name.find("/")
    return name[:slash + 1] if slash >= 0 else None


def main():
    carried = set()
    with open(os.path.join(REPO, "data", "prefixes.txt"), "r",
              encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                carried.add(line)
    # A directory is carried if the list holds it, or holds any deeper cut of it.
    carried_dirs = set()
    for c in carried:
        h = head_of(c)
        if h:
            carried_dirs.add(h)

    pub, conf = Counter(), Counter()

    for fn in PUBLISHED:
        p = os.path.join(REPO, "cod-name-db", "csv", fn)
        if not os.path.exists(p):
            continue
        for n in names_from_csv(p):
            h = head_of(n)
            if h:
                pub[h] += 1

    for p in glob.glob(os.path.join(REPO, "findings", "*", "*.txt")):
        for n in names_from_findings(p):
            h = head_of(n)
            if h:
                conf[h] += 1

    # The two vocabularies are separate files and must be judged separately:
    # sound names go to data/sound.prefixes.txt, everything else to prefixes.txt.
    GENERAL = ("image", "material", "xmodel", "xanim")
    per_type = {}
    for p in glob.glob(os.path.join(REPO, "findings", "*", "*.txt")):
        t = os.path.splitext(os.path.basename(p))[0]
        if t not in GENERAL:
            continue
        c = per_type.setdefault(t, Counter())
        for n in names_from_findings(p):
            h = head_of(n)
            if h:
                c[h] += 1

    print("=== the four general types only (these use data/prefixes.txt) ===")
    for t in GENERAL:
        c = per_type.get(t, Counter())
        miss = [(v, h) for h, v in c.items() if h not in carried_dirs]
        miss.sort(reverse=True)
        print("%-9s %7d confirmed names in %2d dirs; %2d uncarried, heading %d"
              % (t, sum(c.values()), len(c), len(miss), sum(m[0] for m in miss)))
        for v, h in miss[:8]:
            print("        %-14s %7d" % (h, v))
    print()

    allheads = set(pub) | set(conf)
    print("=== every type, published tables and confirmed together ===")
    print("directory heads observed: %d   carried by data/prefixes.txt: %d"
          % (len(allheads), len(carried_dirs & allheads)))
    print()
    rows = []
    for h in allheads:
        rows.append((pub[h] + conf[h], pub[h], conf[h], h, h in carried_dirs))
    rows.sort(reverse=True)

    print("%-22s %10s %10s   %s" % ("directory", "published", "confirmed", "carried?"))
    for total, p, c, h, ok in rows[:45]:
        print("%-22s %10d %10d   %s" % (h, p, c, "yes" if ok else "  <-- NO"))

    missing = [(t, p, c, h) for t, p, c, h, ok in rows if not ok]
    print()
    print("%d of %d observed directories are NOT carried, heading %d published "
          "and %d confirmed names."
          % (len(missing), len(allheads),
             sum(m[1] for m in missing), sum(m[2] for m in missing)))
    print()
    print("uncarried directories, best first:")
    for t, p, c, h in missing[:30]:
        print("   %-22s published %8d   confirmed %8d" % (h, p, c))


if __name__ == "__main__":
    main()
