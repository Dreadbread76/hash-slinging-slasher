"""Remove lowercase vowels from known non-sound basenames."""
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
for name in sorted(names):
    d, sep, b = name.rpartition("/")
    if not sep:
        d, b = "", name
    if "." in b or not any(c in "aeiou" for c in b):
        continue
    out = "".join(c for c in b if c not in "aeiou")
    if not out:
        continue
    candidate = (d + "/" if d else "") + out
    if candidate != name:
        print(candidate)
