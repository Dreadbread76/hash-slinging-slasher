"""Replace a two-token block only with blocks observed before the same five-token suffix.

Run:
    python contrib/suffix_block_precedents.py | bin\\windows\\confirm_list.exe - ^
        --label "two-token per-suffix precedents" --script contrib/suffix_block_precedents.py

Reads the published tables and confirmed names through ``scripts/snapshot.py`` and writes
candidate names, one per line, to standard output.  Reusable: it learns the contexts again
from the current corpus on every run.

The method preserves each name's directory, arbitrary earlier prefix, and final five tokens.
It only replaces the two tokens immediately before that suffix with a two-token block that was
already observed before *that exact suffix*.  The one-token mirror in ``precedents.py`` returned
73 names on Cold War; this is a tighter, two-token local relation rather than a global splice.
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
    "fnv1a_soundbanks_aliases",
)
SUFFIX_TOKENS = 5
MOST_BLOCKS = 16


def known_names():
    names = []
    for table in TABLES:
        names.extend(snapshot.table_names(table))
    names.extend(snapshot.confirmed_names())
    return {name.strip().lower().replace("\\\\", "/") for name in names if name.strip()}


def split(name):
    """Keep a short path directory separate, as the name hash requires it."""
    head, sep, rest = name.partition("/")
    if sep and len(head) <= 6 and "_" not in head:
        return head + "/", rest.split("_")
    return "", name.split("_")


def context(parts, suffix_tokens):
    return "_" + "_".join(parts[-suffix_tokens:])


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--suffix-tokens", type=int, default=SUFFIX_TOKENS)
    parser.add_argument("--most", type=int, default=MOST_BLOCKS)
    parser.add_argument("--count", action="store_true", help="count unique candidates and stop")
    options = parser.parse_args(argv)
    if options.suffix_tokens < 1 or options.most < 1:
        parser.error("--suffix-tokens and --most must be positive")

    names = known_names()
    blocks = collections.defaultdict(collections.Counter)
    for name in names:
        _, parts = split(name)
        if len(parts) < options.suffix_tokens + 2:
            continue
        blocks[context(parts, options.suffix_tokens)][tuple(parts[-options.suffix_tokens - 2 : -options.suffix_tokens])] += 1

    offered = {
        tail: [block for block, _ in counts.most_common(options.most)]
        for tail, counts in blocks.items()
        if len(counts) >= 2
    }
    candidates = set()
    controls = 0
    for name in names:
        directory, parts = split(name)
        if len(parts) < options.suffix_tokens + 2:
            continue
        tail = context(parts, options.suffix_tokens)
        choices = offered.get(tail)
        if not choices:
            continue
        old = tuple(parts[-options.suffix_tokens - 2 : -options.suffix_tokens])
        prefix = parts[: -options.suffix_tokens - 2]
        suffix = parts[-options.suffix_tokens:]
        for block in choices:
            rebuilt = directory + "_".join(prefix + list(block) + suffix)
            if rebuilt in names:
                controls += 1
            if block != old:
                candidates.add(rebuilt)

    print(f"known names: {len(names):,}", file=sys.stderr)
    print(f"suffix contexts with two blocks: {len(offered):,}", file=sys.stderr)
    print(f"known-name controls: {controls:,}", file=sys.stderr)
    print(f"unique unseen-or-known candidates: {len(candidates):,}", file=sys.stderr)
    if not options.count:
        sys.stdout.write("\n".join(candidates))
        if candidates:
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
