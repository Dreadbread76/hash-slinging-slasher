"""Recombine known Cold War names by taking underscore tokens from alternating ends."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
for name in sorted(names):
    if not name:
        continue
    slash, sep, base = name.rpartition("/")
    if not sep:
        slash, base = "", name
    tokens = base.split("_")
    out = []
    lo, hi = 0, len(tokens) - 1
    take_left = True
    while lo <= hi:
        if take_left:
            out.append(tokens[lo]); lo += 1
        else:
            out.append(tokens[hi]); hi -= 1
        take_left = not take_left
    candidate = "_".join(out)
    yield_name = (slash + "/" if slash else "") + candidate
    if yield_name != name and len(tokens) >= 3:
        print(yield_name)
