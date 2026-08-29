"""Interleave vowel and non-vowel basename character streams."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot
tables = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")
known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*tables) if n.strip()}
for kind in ("model", "material", "image", "anim"):
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind=kind) if n.strip())
out = set()
for name in known:
    directory, _, base = name.rpartition("/")
    if len(base) < 5 or "." in base:
        continue
    vowels = [c for c in base if c in "aeiou"]
    other = [c for c in base if c not in "aeiou"]
    merged = []
    for i in range(max(len(vowels), len(other))):
        if i < len(vowels): merged.append(vowels[i])
        if i < len(other): merged.append(other[i])
    out.add((directory + "/" if directory else "") + "".join(merged))
out.difference_update(known)
print(f"{len(known):,} seeds, {len(out):,} candidates", file=sys.stderr)
for candidate in sorted(out): print(candidate)
