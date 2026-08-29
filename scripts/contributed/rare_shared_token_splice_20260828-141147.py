"""Splice a head and tail at a token shared by a small family of real names.

This is narrower than the exhausted all-heads x all-tails splice: only tokens occurring in
2--12 names of the same type are crossed, and the two source names must both contain that token.
"""
import argparse
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = {
    "material": ("fnv1a_xmaterials",),
    "image": ("fnv1a_ximages",),
    "xmodel": ("fnv1a_xmodels",),
    "xanim": ("fnv1a_xanims",),
    "sound_alias": ("fnv1a_soundbanks_aliases",),
}
TOKEN = re.compile(r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9-]{2,})(?![A-Za-z0-9])")


def names(kind):
    values = set(snapshot.table_names(*TABLES[kind]))
    values.update(snapshot.confirmed_names(kind))
    return {n.strip().lower().replace("\\", "/") for n in values if n.strip()}


def candidates(kind):
    known = names(kind)
    by_token = collections.defaultdict(list)
    for name in known:
        for token in set(TOKEN.findall(name)):
            by_token[token].append(name)
    for token, family in sorted(by_token.items()):
        if not 2 <= len(family) <= 12:
            continue
        pieces = []
        for name in family:
            for match in TOKEN.finditer(name):
                if match.group(1) == token:
                    pieces.append((name[: match.start()], name[match.start() :]))
        for head, _ in pieces:
            for _, tail in pieces:
                candidate = head + tail
                if candidate not in known:
                    yield candidate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=sorted(TABLES), default=None)
    parser.add_argument("--size", action="store_true")
    args = parser.parse_args()
    kinds = [args.kind] if args.kind else sorted(TABLES)
    all_candidates = set()
    for kind in kinds:
        current = set(candidates(kind))
        print("%s: %s candidates" % (kind, format(len(current), ",")), file=sys.stderr)
        all_candidates.update(current)
    if args.size:
        print("total: %s candidates" % format(len(all_candidates), ","))
    else:
        for candidate in sorted(all_candidates):
            print(candidate)


if __name__ == "__main__":
    main()
