r"""Relations mined out of the corpus instead of guessed one at a time -- the finished version.

**This supersedes `mined_subs.py`.** That file is the first cut of the same idea and is carried in
an earlier pull request; `submit` will not send an updated copy of a script it has already sent, so
the two extensions measured after it went up -- `--classes` and `--indels` -- live here. Prefer
this file; `mined_subs.py` is kept only because run records name it as their `--script`.

Measured 2026-08-25, both games: pairwise **716**, equivalence classes **192 more on Black Ops 4
alone**. See METHODS.md method 35.



    python contrib/mined_axes.py --top 400 | bin/windows/confirm_list.exe - \
        --label "corpus-mined substitutions" --script contrib/mined_axes.py

    python contrib/mined_axes.py --report      just print what it mined, and stop
    python contrib/mined_axes.py --classes     cross each equivalence class instead
    python contrib/mined_axes.py --indels      anchored insertions and deletions too

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

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import snapshot  # noqa: E402

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims",
          "fnv1a_soundbanks_aliases")


def corpus():
    names = set(snapshot.table_names(*TABLES))
    names |= {n.strip() for n in snapshot.confirmed_names() if n.strip()}
    return sorted({n.lower() for n in names if n})


def difference(a, b, where=False):
    """The middles of a and b, once their common prefix and common suffix are removed."""
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[len(a) - 1 - j] == b[len(b) - 1 - j]:
        j += 1
    if where:
        return a[i:len(a) - j], b[i:len(b) - j], i
    return a[i:len(a) - j], b[i:len(b) - j]


def mine(names, longest, indels=False):
    subs = Counter()
    for order in (names, sorted(names, key=lambda s: s[::-1])):
        for left, right in zip(order, order[1:]):
            u, v, at = difference(left, right, where=True)
            if not u and not v:
                continue
            if not u or not v:
                # An insertion or a deletion has no anchor of its own -- there is no way to know
                # where in a name to put it. Borrowing the character in front turns it into an
                # ordinary substitution that can only fire where the corpus saw it fire:
                # inserting `_lod1` after `y` becomes `y` -> `y_lod1`. Without this the whole
                # class is discarded, and `token_edits` only covers the token-boundary case.
                if not indels or at == 0:
                    continue
                anchor = left[at - 1]
                u, v = anchor + u, anchor + v
            if len(u) > longest or len(v) > longest:
                continue
            # The numeric axis is real and already walked properly by `confirm_variants`, which
            # knows a number is a number. Left in, it is nine tenths of the ranking.
            if u.isdigit() and v.isdigit():
                continue
            subs[(u, v)] += 1
    return subs


def classes(subs, min_seen, max_class):
    """The mined pairs are edges of an equivalence class; return every ordered pair in each.

    `miami -> cartel`, `miami -> tank` and `tank -> cartel` are three observations of one axis --
    the map codename -- and the axis has more members than any single pair shows. Taking connected
    components and crossing each one recovers the substitutions the corpus implies but never
    happened to put next to each other in sorted order.

    Multi-character sides only, and that is not a tidiness rule: single letters chain (`a`->`b`,
    `b`->`c`, `c`->`d`) until every letter of the alphabet is one component, which crosses to 650
    substitutions applied at every position of every name and is pure noise. At three characters
    and up the components come out semantically clean -- weapon parts, factions, specialists,
    stances, channel codes -- and the one that does over-merge is visible because it is huge.
    """
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (u, v), count in subs.items():
        if count >= min_seen and len(u) >= 3 and len(v) >= 3:
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv

    groups = {}
    for member in list(parent):
        groups.setdefault(find(member), set()).add(member)

    out = []
    for group in groups.values():
        if len(group) < 2 or len(group) > max_class:
            continue
        members = sorted(group)
        for u in members:
            for v in members:
                if u != v:
                    out.append((u, v, len(members)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=400, help="how many mined substitutions to apply")
    ap.add_argument("--longest", type=int, default=6, help="longest side of a substitution")
    ap.add_argument("--min-seen", type=int, default=20)
    ap.add_argument("--cap", type=int, default=200000, help="candidates per substitution")
    ap.add_argument("--report", action="store_true", help="print the mined table and stop")
    ap.add_argument("--classes", action="store_true",
                    help="cross each equivalence class rather than using the observed pairs only")
    ap.add_argument("--indels", action="store_true",
                    help="also mine insertions and deletions, anchored on the character in front")
    ap.add_argument("--max-class", type=int, default=40,
                    help="drop a component bigger than this -- it has over-merged")
    args = ap.parse_args()

    names = corpus()
    sys.stderr.write("corpus: %s\n" % "{:,}".format(len(names)))
    subs = mine(names, args.longest, args.indels)
    sys.stderr.write("distinct substitutions mined: %s\n" % "{:,}".format(len(subs)))

    if args.classes:
        kept = classes(subs, args.min_seen, args.max_class)
        sys.stderr.write(("substitutions from equivalence classes: %s" + chr(10))
                         % "{:,}".format(len(kept)))
    else:
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
