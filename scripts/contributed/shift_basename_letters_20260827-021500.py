"""Shift alphabetic basename characters forward by one, preserving nonletters."""
import os, sys
_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))
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
