"""Move a boundary character from one token into its neighbour.

This tests names formed by splitting/merging token boundaries, distinct from
separator variants and whole-token character transforms.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
known = set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
rows = []
for raw in known:
    n = raw.lower().replace("\\", "/")
    if "/" not in n or "." in n.rsplit("/", 1)[-1]:
        continue
    d, b = n.rsplit("/", 1)
    t = b.split("_")
    if len(t) >= 3:
        rows.append((d, t))

for d, tokens in sorted(rows)[:50000]:
    for i in range(len(tokens) - 1):
        left, right = tokens[i], tokens[i + 1]
        if len(left) > 1:
            out = list(tokens)
            out[i], out[i + 1] = left[:-1], left[-1] + right
            candidate = d + "/" + "_".join(out)
            if candidate not in known:
                print(candidate)
        if len(right) > 1:
            out = list(tokens)
            out[i], out[i + 1] = left + right[0], right[1:]
            candidate = d + "/" + "_".join(out)
            if candidate not in known:
                print(candidate)
