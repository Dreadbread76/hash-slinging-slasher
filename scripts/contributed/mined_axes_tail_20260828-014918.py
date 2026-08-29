"""Bounded tail band of corpus-mined multi-character substitutions.

This deliberately tests substitutions ranked 401-430 by observed frequency, avoiding the
already-swept high-frequency bands while retaining the corpus-derived relation rather than
inventing a replacement alphabet.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims",
          "fnv1a_soundbanks_aliases")
RANK_START, RANK_END = 400, 430
PER_SUBSTITUTION_CAP = 2000


def corpus():
    names = set(snapshot.table_names(*TABLES))
    names |= {n.strip() for n in snapshot.confirmed_names() if n.strip()}
    return sorted({n.lower() for n in names if n})


def difference(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return a[i:len(a) - j], b[i:len(b) - j]


def mine(names):
    counts = {}
    for order in (names, sorted(names, key=lambda s: s[::-1])):
        for left, right in zip(order, order[1:]):
            old, new = difference(left, right)
            if not old or not new or old.isdigit() and new.isdigit():
                continue
            if len(old) > 6 or len(new) > 6:
                continue
            counts[(old, new)] = counts.get((old, new), 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def main():
    names = corpus()
    known = set(names)
    ranked = mine(names)
    band = [(pair, count) for pair, count in ranked if count >= 20][RANK_START:RANK_END]
    seen = set()
    emitted = 0
    for (old, new), _count in band:
        made = 0
        for name in names:
            at = name.find(old)
            while at >= 0 and made < PER_SUBSTITUTION_CAP:
                candidate = name[:at] + new + name[at + len(old):]
                if candidate not in known and candidate not in seen:
                    seen.add(candidate)
                    print(candidate)
                    emitted += 1
                    made += 1
                at = name.find(old, at + 1)
            if made >= PER_SUBSTITUTION_CAP:
                break
    print(f"rank band {RANK_START + 1}-{RANK_END}: {len(band)} substitutions; {emitted} candidates",
          file=sys.stderr)


if __name__ == "__main__":
    main()
