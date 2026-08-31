"""Splice known basename prefixes and suffixes at rare shared tokens.

Only vocabulary already present in the selected asset type is used. Very common tokens are
excluded because their quadratic cross-product is both noisy and uninformative.
"""
import collections
import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
while root != os.path.dirname(root) and not os.path.isfile(os.path.join(root, "scripts", "snapshot.py")):
    root = os.path.dirname(root)
sys.path.insert(0, os.path.join(root, "scripts"))
import snapshot

TYPES = {
    "model": ("fnv1a_xmodels", "xmodel"),
    "material": ("fnv1a_xmaterials", "material"),
    "image": ("fnv1a_ximages", "image"),
    "anim": ("fnv1a_xanims", "xanim"),
}
kind = "material"
if "--type" in sys.argv:
    kind = sys.argv[sys.argv.index("--type") + 1]
if kind not in TYPES:
    raise SystemExit("--type must be one of: " + ", ".join(sorted(TYPES)))

table, confirmed_type = TYPES[kind]
known = set()
for name in list(snapshot.table_names(table)) + list(snapshot.confirmed_names(confirmed_type)):
    name = name.strip().lower().replace("\\", "/")
    if name:
        known.add(name)

parsed = []
occurrences = collections.defaultdict(list)
for name in sorted(known):
    directory, _, basename = name.rpartition("/")
    tokens = basename.split("_")
    if len(tokens) < 3 or len(tokens) > 12:
        continue
    item = (directory + "/" if directory else "", tokens)
    parsed.append(item)
    for pos, token in enumerate(tokens):
        occurrences[token].append((len(parsed) - 1, pos))

seen = set()
counting = "--count" in sys.argv
for token, refs in sorted(occurrences.items()):
    if len(refs) < 2 or len(refs) > 40:
        continue
    for ai, apos in refs:
        adir, atokens = parsed[ai]
        if apos == 0:
            continue
        for bi, bpos in refs:
            if ai == bi or bpos >= len(parsed[bi][1]) - 1:
                continue
            _, btokens = parsed[bi]
            candidate = adir + "_".join(atokens[: apos + 1] + btokens[bpos + 1 :])
            if candidate not in known and candidate not in seen:
                seen.add(candidate)
                if not counting:
                    print(candidate)

if counting:
    print(len(seen), file=sys.stderr)
