"""Try adjacent underscore-token order swaps on known names.

This probes the untested token_order idea without inventing vocabulary: every candidate is made
from a confirmed or published name by swapping one adjacent pair in its basename.
"""
import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
while root != os.path.dirname(root) and not os.path.isfile(os.path.join(root, "scripts", "snapshot.py")):
    root = os.path.dirname(root)
sys.path.insert(0, os.path.join(root, "scripts"))
import snapshot

TABLES = {
    "model": ("fnv1a_xmodels", "xmodel"),
    "material": ("fnv1a_xmaterials", "material"),
    "image": ("fnv1a_ximages", "image"),
    "anim": ("fnv1a_xanims", "xanim"),
}

kind = "model"
if "--type" in sys.argv:
    kind = sys.argv[sys.argv.index("--type") + 1]
if kind not in TABLES:
    raise SystemExit("--type must be one of: " + ", ".join(sorted(TABLES)))

table, confirmed_type = TABLES[kind]
known = set()
for name in list(snapshot.table_names(table)) + list(snapshot.confirmed_names(confirmed_type)):
    name = name.strip().lower().replace("\\", "/")
    if name:
        known.add(name)

seen = set()
counting = "--count" in sys.argv
for name in sorted(known):
    directory, _, basename = name.rpartition("/")
    tokens = basename.split("_")
    if len(tokens) < 3:
        continue
    for i in range(len(tokens) - 1):
        swapped = tokens[:]
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        candidate = (directory + "/" if directory else "") + "_".join(swapped)
        if candidate not in known and candidate not in seen:
            seen.add(candidate)
            if not counting:
                print(candidate)

if counting:
    print(len(seen), file=sys.stderr)
