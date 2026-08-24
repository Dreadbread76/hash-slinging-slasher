"""Is token ORDER a free parameter in these names, or is the convention positional?

METHODS.md lists `token_order.py` under "Candidates worth building" with the check
that decides it already written down:

    permute two adjacent middle tokens. Nothing here reorders anything.
    Measure: do any permutations of confirmed names already appear in the
    tables? If none do, the convention is stable and this finds nothing.

That is the whole measurement, and it is decisive in both directions:

  * If swapping two adjacent middle tokens of a KNOWN name lands on ANOTHER
    KNOWN name at any appreciable rate, then the naming does not fix token
    order, both spellings get used, and every known name is a candidate
    generator for a sibling nothing here can currently emit -- the general
    search composes begin+stem+end and cannot reorder a middle, `slotswap`
    substitutes a middle but preserves its position, `confirm_variants` only
    moves numbers.

  * If it essentially never happens, the convention is stable and the method is
    dead. Writing that down costs the next contributor nothing and saves them
    the build.

Read-only: hashes nothing, writes nothing, prints a rate.
"""
import os, glob, random
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# BO4/BOCW only -- the _v2 tables are other titles under the IW offset.
PUBLISHED = ["fnv1a_xmaterials.csv", "fnv1a_ximages.csv",
             "fnv1a_xmodels.csv", "fnv1a_xanims.csv"]
GENERAL = ("image", "material", "xmodel", "xanim")

# streamkey and the other low-value pools are excluded by name: they are
# machine-generated and would swamp any rate measured here. See CLAUDE.md §5.
SKIP_POOLS = {"streamkey", "xmodelmesh", "localizeentry"}


def load():
    names = set()
    for fn in PUBLISHED:
        p = os.path.join(REPO, "cod-name-db", "csv", fn)
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                c = line.find(",")
                if c >= 0:
                    names.add(line[c + 1:])
    confirmed = set()
    for p in glob.glob(os.path.join(REPO, "findings", "*", "*.txt")):
        pool = os.path.splitext(os.path.basename(p))[0]
        if pool not in GENERAL or pool in SKIP_POOLS:
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                if not line:
                    continue
                c = line.find(",")
                confirmed.add(line[c + 1:] if c >= 0 else line)
    return names, confirmed


def middles_swapped(name):
    """Yield the name with each adjacent pair of MIDDLE tokens transposed.

    The first and last tokens are held fixed: the first carries the directory
    and type code (`mc/mtl_`), the last is the channel/variant suffix, and both
    are already reachable by begin/end composition. Only the middle is ground
    nothing here can currently reorder.
    """
    parts = name.split("_")
    if len(parts) < 4:
        return
    for i in range(1, len(parts) - 2):
        if parts[i] == parts[i + 1]:
            continue
        swapped = parts[:i] + [parts[i + 1], parts[i]] + parts[i + 2:]
        yield "_".join(swapped)


def main():
    published, confirmed = load()
    known = published | confirmed
    print("known names loaded: %d published, %d confirmed, %d distinct"
          % (len(published), len(confirmed), len(known)))

    # Measure on the confirmed corpus (what this project actually recovers) and
    # on a sample of published, so a difference between the two shows up.
    for label, corpus in (("confirmed", confirmed), ("published", published)):
        pool = list(corpus)
        if len(pool) > 120000:
            random.seed(1234)
            pool = random.sample(pool, 120000)
        tried = hits = 0
        eligible = 0
        examples = []
        for name in pool:
            got = False
            for perm in middles_swapped(name):
                tried += 1
                if perm in known and perm != name:
                    hits += 1
                    got = True
                    if len(examples) < 10:
                        examples.append((name, perm))
            if got:
                eligible += 1
        if tried == 0:
            print("%-10s no eligible names" % label)
            continue
        print()
        print("%-10s %d names sampled, %d permutations tried, %d landed on a known name"
              % (label, len(pool), tried, hits))
        print("%-10s rate: 1 per %s permutations; %d names had at least one"
              % ("", ("%.0f" % (tried / hits)) if hits else "never", eligible))
        for a, b in examples:
            print("     %s\n  -> %s" % (a, b))


if __name__ == "__main__":
    main()
