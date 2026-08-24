"""Where in a name does a ONE-CHARACTER difference actually happen?

`tails.py` replaces the last k characters and `tails.py --head` the first k, and
between them they are the two best-measured methods here. Both work on an *end*.
Nothing in the registry substitutes a single character in the **middle**:
`slotswap` replaces a whole token and keeps its slot, `token_edits` adds and
removes whole tokens, `confirm_variants` moves only numbers.

Whether that gap is worth filling depends on where one-character differences
actually occur, so this measures it exactly rather than sampling substitutions:

For every known name and every character position, blank that position. Two names
that differ in exactly one character collapse to the same blanked form. Counting
pairs per blanked form therefore counts one-character-apart pairs **exactly**,
and bucketing by position says whether those pairs live at the ends (where
`tails` and `heads` already reach) or in the middle (where nothing does).

`dist_from_end` is the number that matters: `tails --length 4` already reaches
every substitution at distance 0-3, so only pairs at distance >= 4 are new ground.

Read-only. Prints a distribution.
"""
import os, glob, random, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISHED = ["fnv1a_xmaterials.csv", "fnv1a_ximages.csv",
             "fnv1a_xmodels.csv", "fnv1a_xanims.csv"]
GENERAL = ("image", "material", "xmodel", "xanim")

SAMPLE = 120000          # keeps the blanked-form table inside memory
TAILS_REACH = 4          # what `tails --length 4` already covers


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
    names = load()
    sys.stderr.write("known names: %d\n" % len(names))
    pool = list(names)
    if len(pool) > SAMPLE:
        random.seed(20260825)
        pool = random.sample(pool, SAMPLE)

    # blanked form -> how many sampled names collapse to it
    forms = Counter()
    for name in pool:
        n = len(name)
        for i in range(n):
            forms[hash((name[:i], name[i + 1:]))] += 1

    # A blanked form shared by m names is C(m,2) one-character-apart pairs.
    pairs = sum(m * (m - 1) // 2 for m in forms.values() if m > 1)
    sys.stderr.write("blanked forms: %d\n" % len(forms))
    print("sampled names: %d" % len(pool))
    print("one-character-apart pairs among them: %d" % pairs)
    print()

    # Now bucket those pairs by distance from the end, which is what decides
    # whether `tails` already reaches them.
    shared = {k for k, m in forms.items() if m > 1}
    bydist = Counter()
    bychar = Counter()
    examples = {}
    for name in pool:
        n = len(name)
        for i in range(n):
            key = hash((name[:i], name[i + 1:]))
            if key in shared:
                d = n - 1 - i
                bydist[d] += 1
                bychar[name[i]] += 1
                if d >= TAILS_REACH and len(examples) < 12:
                    examples.setdefault(d, name)

    total = sum(bydist.values())
    reachable = sum(v for d, v in bydist.items() if d < TAILS_REACH)
    print("%-16s %10s  %s" % ("dist from end", "members", "share"))
    for d in sorted(bydist)[:16]:
        mark = "  <- tails --length 4 reaches this" if d < TAILS_REACH else ""
        print("%-16d %10d  %5.1f%%%s" % (d, bydist[d], 100.0 * bydist[d] / total, mark))
    print()
    print("members of a one-character-apart pair: %d" % total)
    print("  within the last %d characters (tails reaches): %d (%.1f%%)"
          % (TAILS_REACH, reachable, 100.0 * reachable / total))
    print("  deeper in the name (NOTHING reaches):        %d (%.1f%%)"
          % (total - reachable, 100.0 * (total - reachable) / total))
    print()
    print("the character that varies, commonest first:")
    for ch, n in bychar.most_common(14):
        print("   %r %d" % (ch, n))
    print()
    print("examples of names varying deep in the middle:")
    for d in sorted(examples)[:6]:
        print("   dist %-3d %s" % (d, examples[d]))


if __name__ == "__main__":
    main()
