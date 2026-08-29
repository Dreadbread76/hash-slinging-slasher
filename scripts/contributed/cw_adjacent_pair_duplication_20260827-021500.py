"""Duplicate an adjacent underscore-token pair in known non-sound asset names.

Unlike whole-basename duplication or single-token edits, this probes repeated
two-token construction (common in generated variant/family names).  The bound
keeps the reconnaissance seeded and reproducible.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
known = set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
names = []
for raw in known:
    n = raw.lower().replace("\\", "/")
    if "/" not in n or "." in n.rsplit("/", 1)[-1]:
        continue
    d, b = n.rsplit("/", 1)
    tok = b.split("_")
    if len(tok) >= 4:
        names.append((d, tok))

for d, tok in sorted(names)[:50000]:
    for i in range(len(tok) - 1):
        out = tok[:i] + tok[i:i+2] + tok[i:]
        candidate = d + "/" + "_".join(out)
        if candidate not in known:
            print(candidate)
