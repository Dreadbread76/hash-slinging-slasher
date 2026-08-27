"""Swap the first and last character of each individual basename token.

This probes a distinct typo/variant axis from whole-token substitutions and
the previously mined character rotations/reversals.
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
    for i, token in enumerate(tokens):
        if len(token) < 2 or token[0] == token[-1]:
            continue
        changed = list(tokens)
        changed[i] = token[-1] + token[1:-1] + token[0]
        candidate = d + "/" + "_".join(changed)
        if candidate not in known:
            print(candidate)
