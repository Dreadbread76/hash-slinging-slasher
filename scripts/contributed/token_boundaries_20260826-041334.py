"""Try observed merged-versus-separated token spellings.

    python contrib/token_boundaries.py --count
    python contrib/token_boundaries.py | target\\release\\confirm_list.exe - --game BLKOPSCW \\
        --label "observed token-boundary variants" --script contrib/token_boundaries.py --anyway

Names in this corpus are conventionally underscore-separated, but some concepts are spelled both
ways: a token pair such as ``dual_optic`` can also be a single token, ``dualoptic``.  The existing
token-edit generator inserts, deletes and substitutes whole tokens; it cannot change this boundary.

This generator is deliberately bounded by observed vocabulary.  A split is offered only when both
the fused token and its two-token spelling occur in real, known names.  That makes it a test of a
measured naming convention rather than arbitrary word segmentation.

It reads the five target tables and confirmed submissions through ``snapshot.py`` and writes
candidate names to stdout.  ``--count`` reports candidate and positive-control counts without
writing candidates.  Reusable: new confirmed names can supply new observed boundary pairs.
"""
import argparse
import collections
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import snapshot


TABLES = (
    "fnv1a_xmodels",
    "fnv1a_xmaterials",
    "fnv1a_ximages",
    "fnv1a_xanims",
    "fnv1a_xsounds",
    "fnv1a_soundbanks_aliases",
)


def split(name):
    """Keep a directory whole; token boundaries only mean underscores."""
    directory, marker, base = name.rpartition("/")
    return (directory + marker if marker else ""), tuple(part for part in base.split("_") if part)


def names():
    found = set(snapshot.table_names(*TABLES))
    found.update(snapshot.confirmed_names())
    return {
        name.strip().lower().replace("\\\\", "/")
        for name in found
        if name.strip() and len(name) <= 160
    }


def boundary_pairs(parsed):
    """Return only pair <-> fused spellings both evidenced by the corpus."""
    tokens = collections.Counter()
    pairs = collections.Counter()
    for _, parts in parsed:
        tokens.update(parts)
        pairs.update(zip(parts, parts[1:]))

    fused_to_pairs = collections.defaultdict(list)
    pair_to_fused = collections.defaultdict(list)
    for pair, seen in pairs.items():
        fused = "".join(pair)
        # A once-seen pair or a once-seen fused spelling is too close to a typo.  These floors
        # are a precision gate, not a ranking; all qualifying alternatives are carried.
        if seen >= 2 and tokens[fused] >= 2:
            pair_to_fused[pair].append(fused)
            fused_to_pairs[fused].append(pair)
    return pair_to_fused, fused_to_pairs


def candidates(parsed, known, pair_to_fused, fused_to_pairs):
    seen = set()
    controls = 0
    for directory, parts in parsed:
        for index in range(len(parts) - 1):
            for fused in pair_to_fused.get((parts[index], parts[index + 1]), ()):
                candidate = directory + "_".join(parts[:index] + (fused,) + parts[index + 2:])
                if candidate in known:
                    controls += 1
                elif candidate not in seen:
                    seen.add(candidate)
                    yield candidate

        for index, token in enumerate(parts):
            for left, right in fused_to_pairs.get(token, ()):
                candidate = directory + "_".join(parts[:index] + (left, right) + parts[index + 1:])
                if candidate in known:
                    controls += 1
                elif candidate not in seen:
                    seen.add(candidate)
                    yield candidate

    return controls


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", action="store_true", help="report sizing and known-name controls")
    options = parser.parse_args(argv)

    known = names()
    parsed = [split(name) for name in known]
    pair_to_fused, fused_to_pairs = boundary_pairs(parsed)

    # Materialise once so that `--count` has an exact candidate total and the generator remains
    # deterministic for the run fingerprint.
    output = list(candidates(parsed, known, pair_to_fused, fused_to_pairs))
    controls = 0
    for directory, parts in parsed:
        for index in range(len(parts) - 1):
            for fused in pair_to_fused.get((parts[index], parts[index + 1]), ()):
                if directory + "_".join(parts[:index] + (fused,) + parts[index + 2:]) in known:
                    controls += 1
        for index, token in enumerate(parts):
            for left, right in fused_to_pairs.get(token, ()):
                if directory + "_".join(parts[:index] + (left, right) + parts[index + 1:]) in known:
                    controls += 1

    print(
        "%s known names; %s observed boundary pairs; %s known-name controls; %s new candidates"
        % (format(len(known), ","), format(len(pair_to_fused), ","), format(controls, ","), format(len(output), ",")),
        file=sys.stderr,
    )
    if options.count:
        return 0
    for candidate in sorted(output):
        print(candidate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
