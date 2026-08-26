"""What characters actually occur in the last few characters of a name?

`tails.py` enumerates every k-character string over one alphabet of 37 characters
-- the ones names end in -- which is what makes the ladder explode: k=4 is 1.87 M
endings, k=5 is 69.3 M and about 42 T candidates, a seven-hour pass per game.

But that alphabet is measured over the last character only and then applied to
all k positions, and the positions are not alike. The final character of a name
is a channel code or a digit; five from the end is far more often `_`. Enumerating
all 37 at every position spends most of the pass on strings the naming never
produces.

So this measures the alphabet **per position**, and reports how small a set covers
99% / 99.9% of real names at each one. The product of those per-position sizes is
what a position-aware k=5 would actually cost.

Read-only. Prints a table.
"""
import os, glob, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISHED = ["fnv1a_xmaterials.csv", "fnv1a_ximages.csv",
             "fnv1a_xmodels.csv", "fnv1a_xanims.csv"]
GENERAL = ("image", "material", "xmodel", "xanim")
K = 5


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


def cover(counter, share):
    """Smallest set of characters covering `share` of occurrences."""
    total = sum(counter.values())
    got, chars = 0, []
    for ch, n in counter.most_common():
        chars.append(ch)
        got += n
        if got >= total * share:
            break
    return chars


def main():
    names = [n for n in load() if len(n) >= K]
    sys.stderr.write("names of length >= %d: %d\n" % (K, len(names)))

    per_pos = [Counter() for _ in range(K)]
    for n in names:
        for j in range(K):
            per_pos[j][n[-(j + 1)]] += 1

    print("position 0 = the final character, %d = %d from the end" % (K - 1, K - 1))
    print()
    print("%-10s %8s %10s %10s   %s" % ("position", "distinct", "99% needs", "99.9% needs", "commonest"))
    sizes99, sizes999 = [], []
    for j in range(K):
        c99 = cover(per_pos[j], 0.99)
        c999 = cover(per_pos[j], 0.999)
        sizes99.append(len(c99))
        sizes999.append(len(c999))
        top = "".join(ch for ch, _ in per_pos[j].most_common(12))
        print("%-10d %8d %10d %10d   %r" % (j, len(per_pos[j]), len(c99), len(c999), top))

    full = 1
    for j in range(K):
        full *= len(per_pos[j])
    p99 = 1
    for s in sizes99:
        p99 *= s
    p999 = 1
    for s in sizes999:
        p999 *= s

    print()
    print("k=%d endings, all characters seen at each position: %s" % (K, "{:,}".format(full)))
    print("k=%d endings, 99%%   alphabet per position:          %s  (%.1fx cheaper)"
          % (K, "{:,}".format(p99), full / float(p99)))
    print("k=%d endings, 99.9%% alphabet per position:          %s  (%.1fx cheaper)"
          % (K, "{:,}".format(p999), full / float(p999)))
    print()
    print("one flat alphabet of 37 at every position (what tails.py does): %s"
          % "{:,}".format(37 ** K))
    print()
    print("the 99%% alphabets, position %d..0 (deepest first) -- this is the ending set:" % (K - 1))
    for j in range(K - 1, -1, -1):
        print("   pos %d  %r" % (j, "".join(sorted(cover(per_pos[j], 0.99)))))


if __name__ == "__main__":
    main()
