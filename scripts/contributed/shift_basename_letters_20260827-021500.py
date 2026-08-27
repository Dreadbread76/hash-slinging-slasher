"""Shift alphabetic basename characters forward by one, preserving nonletters."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
def shift(c):
    if "a" <= c <= "y": return chr(ord(c) + 1)
    if c == "z": return "a"
    return c
for name in sorted(names):
    d, sep, b = name.rpartition("/")
    if not sep:
        d, b = "", name
    if len(b) < 4 or "." in b:
        continue
    candidate = (d + "/" if d else "") + "".join(shift(c) for c in b)
    if candidate != name:
        print(candidate)
