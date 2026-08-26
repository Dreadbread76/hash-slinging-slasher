"""Test and generate locally evidenced adjacent-token order variants.

    python contrib/adjacent_token_order.py --measure
    python contrib/adjacent_token_order.py | bin\\windows\\confirm_list.exe - \
        --label "locally evidenced adjacent token order" \
        --script contrib/adjacent_token_order.py

This asks a relation none of the substitution methods asks: whether two adjacent interior
tokens can reverse position.  It only emits a swap when the same ordered token pair occurs
both ways elsewhere in real names, so candidates are recombinations of observed conventions
rather than arbitrary word permutations.

Reads the five target tables and confirmed findings through scripts/snapshot.py.  Writes only
candidate names on standard output; --measure writes a positive-control summary to stderr.
Reusable: rerun when the confirmed corpus grows.
"""
import argparse
import collections
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))

import snapshot

TABLES = (
    "fnv1a_ximages",
    "fnv1a_xmaterials",
    "fnv1a_xmodels",
    "fnv1a_xanims",
    "fnv1a_soundbanks_aliases",
    "fnv1a_xsounds",
)


def names():
    known = set()
    for table in TABLES:
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table))
    for kind in ("image", "material", "xmodel", "xanim", "sound_alias", "sound_asset"):
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind))
    return {n for n in known if n}


def pairs(known):
    observed = collections.Counter()
    for name in known:
        tokens = name.split("_")
        # The first and final tokens encode directories/prefixes and channels/variants often
        # enough that swapping them is a different spelling relation, not token order.
        for index in range(1, len(tokens) - 2):
            if tokens[index] and tokens[index + 1]:
                observed[(tokens[index], tokens[index + 1])] += 1
    return observed


def candidates(known, reversible):
    for name in known:
        tokens = name.split("_")
        for index in range(1, len(tokens) - 2):
            pair = (tokens[index], tokens[index + 1])
            if pair not in reversible:
                continue
            changed = tokens[:]
            changed[index], changed[index + 1] = changed[index + 1], changed[index]
            candidate = "_".join(changed)
            if candidate not in known:
                yield candidate


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--measure", action="store_true")
    options = parser.parse_args(argv)

    known = names()
    observed = pairs(known)
    reversible = {pair for pair in observed if (pair[1], pair[0]) in observed}
    offered = set(candidates(known, reversible))
    controls = sum(count for pair, count in observed.items() if pair in reversible)

    print(
        "%s real names; %s interior ordered pairs; %s reversible pairs; "
        "%s observed-name controls; %s unseen candidates"
        % tuple(format(value, ",") for value in (
            len(known), len(observed), len(reversible), controls, len(offered)
        )),
        file=sys.stderr,
    )
    if not options.measure:
        sys.stdout.write("\n".join(sorted(offered)))
        if offered:
            sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
