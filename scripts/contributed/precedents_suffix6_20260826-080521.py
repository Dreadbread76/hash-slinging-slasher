"""Offer each six-token suffix the one-token precedents measured before that exact suffix.

Run:
    python contrib/precedents_suffix6.py | bin\\windows\\confirm_list.exe - ^
        --label "per-suffix precedents, six-token tails" --script contrib/precedents_suffix6.py

This is a reusable, stricter continuation of ``scripts/precedents.py``.  It reads the current
published and confirmed corpus and writes candidates to standard output; no working data is
written.  Six-token tails are deliberately kept separate from the established five-token pass so
the search reaches a distinct, more specific contextual ground.
"""
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))

import argparse
import collections
import precedents


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--most", type=int, default=precedents.MOST_PRECEDENTS)
    parser.add_argument("--count", action="store_true")
    options = parser.parse_args(argv)
    names = precedents.known_names()
    before = precedents.measure(names)
    suffixes = collections.defaultdict(collections.Counter)
    for name in names:
        directory, parts = precedents.split(name)
        if len(parts) < 8:
            continue
        suffix = "_" + "_".join(parts[-6:])
        suffixes[suffix][parts[-7]] += 1
    offered = {
        suffix: [token for token, _ in counts.most_common(options.most)]
        for suffix, counts in suffixes.items()
        if sum(counts.values()) >= precedents.LEAST_SEEN
    }
    candidates = set()
    for name in names:
        directory, parts = precedents.split(name)
        if len(parts) < 8:
            continue
        suffix = "_" + "_".join(parts[-6:])
        for token in offered.get(suffix, ()):
            if token == parts[-7]:
                continue
            candidates.add(directory + "_".join(parts[:-7] + [token] + parts[-6:]))
    print(f"known names: {len(names):,}", file=sys.stderr)
    print(f"six-token suffixes with precedents: {len(offered):,}", file=sys.stderr)
    print(f"unique candidates: {len(candidates):,}", file=sys.stderr)
    if not options.count:
        sys.stdout.write("\n".join(candidates))
        if candidates:
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
