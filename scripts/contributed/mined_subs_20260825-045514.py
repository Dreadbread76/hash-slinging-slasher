r"""Relations mined out of the corpus instead of guessed one at a time.

    python contrib/mined_subs.py --top 400 | bin/windows/confirm_list.exe - \
        --label "corpus-mined substitutions" --script contrib/mined_subs.py

    python contrib/mined_subs.py --report      just print what it mined, and stop

## The gap this exists for

Every relation this project exploits was **thought of by a person**, one at a time, and then
built: image siblings, image channels, materials from image cores, the language codes, family
gaps, token order, numeric repadding. `derive_closure.py` is a list of seven such guesses. The
good ones are the densest methods here -- `final_byte` at 1 per 18, siblings at 1 per 394 -- so
the guessing works. What nothing does is **ask the corpus which relations exist.**

It can be asked directly, and cheaply. Sort every known name; two names that sit next to each
other in sorted order usually share a long prefix, so the part where they differ is a
substitution the naming actually performs. Do it again over the names sorted by their *reverse*
to catch the pairs that share a suffix instead. Count the substitutions. The ones that recur are
the game's own axes.

Run over 1,531,805 names on 2026-08-25 it recovers, unprompted and in order:

    '1' -> '2', '0' -> '1', ...     the numeric axis      (confirm_variants, families --gaps)
    ''  -> 'i_'                     the image sibling     (image siblings)
    'i' -> 'mtl'                    image <-> material    (materials from image cores)
    'c' -> 'g', 'c' -> 'n', ...     the channel codes     (image channel completion)

which is four of the seven hand-built relations, found without being told they exist. That is the
control: a miner that could not re-derive the known axes would not be worth pointing at the
unknown ones.

And then it keeps going, into axes nothing here lists:

    'austr' -> 'milit'   21,450 pairs        'view'    -> 'world'   6,962
    'levati' -> 'chel'    5,760              'morocc'  -> 'casin'   5,177

Those are **map codenames**. The same asset exists under several maps, and no method here
substitutes one map for another -- `map_sets.py` was proposed for something adjacent and never
built, and `slotswap` cannot reach it because these are not whole tokens (`austr` is a cut of
`australia`, sitting inside a longer token).

## How it generates

The top `--top` substitutions by evidence, applied to every known name that contains the left
side, one occurrence at a time. Pure-digit substitutions are dropped: they are the numeric axis,
which `confirm_variants` already walks properly, and including them buries everything else.
Candidates already in the corpus are dropped.

Each candidate is therefore one substitution away from a name known to be real, which is the
shape METHODS records as live -- and unlike `splice`, the substitution itself is one the corpus
was observed to perform rather than one the generator invented.
"""
import argparse, os, sys
from collections import Counter

REPO = os.path.dirname(os.path.abspath(__file__))
while REPO != os.path.dirname(REPO) and not os.path.isfile(
    os.path.join(REPO, "scripts", "snapshot.py")
):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import snapshot  # noqa: E402

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims",
          "fnv1a_soundbanks_aliases")


def corpus():
    names = set(snapshot.table_names(*TABLES))
    names |= {n.strip() for n in snapshot.confirmed_names() if n.strip()}
    return sorted({n.lower() for n in names if n})


def difference(a, b):
    """The middles of a and b, once their common prefix and common suffix are removed."""
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[len(a) - 1 - j] == b[len(b) - 1 - j]:
        j += 1
    return a[i:len(a) - j], b[i:len(b) - j]


def mine(names, longest):
    subs = Counter()
    for order in (names, sorted(names, key=lambda s: s[::-1])):
        for left, right in zip(order, order[1:]):
            u, v = difference(left, right)
            # Both sides must be present: an insertion has no anchor, so there is no way to know
            # where in the name to put it, and guessing every position is a different method.
            if not u or not v:
                continue
            if len(u) > longest or len(v) > longest:
                continue
            # The numeric axis is real and already walked properly by `confirm_variants`, which
            # knows a number is a number. Left in, it is nine tenths of the ranking.
            if u.isdigit() and v.isdigit():
                continue
            subs[(u, v)] += 1
    return subs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=400, help="how many mined substitutions to apply")
    ap.add_argument("--longest", type=int, default=6, help="longest side of a substitution")
    ap.add_argument("--min-seen", type=int, default=20)
    ap.add_argument("--cap", type=int, default=200000, help="candidates per substitution")
    ap.add_argument("--report", action="store_true", help="print the mined table and stop")
    args = ap.parse_args()

    names = corpus()
    sys.stderr.write("corpus: %s\n" % "{:,}".format(len(names)))
    subs = mine(names, args.longest)
    sys.stderr.write("distinct substitutions mined: %s\n" % "{:,}".format(len(subs)))

    kept = [(u, v, c) for (u, v), c in subs.most_common() if c >= args.min_seen][:args.top]
    if args.report:
        for u, v, c in kept:
            print("%8d  %-8s -> %s" % (c, u, v))
        return

    known = set(names)
    seen = set()
    emitted = 0
    for u, v, _count in kept:
        made = 0
        for name in names:
            start = name.find(u)
            while start >= 0 and made < args.cap:
                candidate = name[:start] + v + name[start + len(u):]
                if candidate not in known and candidate not in seen:
                    seen.add(candidate)
                    print(candidate)
                    emitted += 1
                    made += 1
                start = name.find(u, start + 1)
            if made >= args.cap:
                break
    sys.stderr.write("substitutions applied: %d   candidates: %s\n"
                     % (len(kept), "{:,}".format(emitted)))


if __name__ == "__main__":
    main()
