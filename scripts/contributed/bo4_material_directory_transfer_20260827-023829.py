"""Transfer observed material basenames across observed material directories."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot
names = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names("fnv1a_xmaterials") if n.strip()}
names.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind="material") if n.strip())
pairs = []
for name in sorted(names):
    directory, sep, base = name.rpartition("/")
    if not sep or "." in base:
        continue
    pairs.append((directory + "/", base))
dirs = sorted({directory for directory, _ in pairs})
bases = sorted({base for _, base in pairs})
out = {directory + base for directory in dirs[:100] for base in bases[:50]}
out.difference_update(names)
print(f"{len(names):,} seeds, {len(out):,} candidates", file=sys.stderr)
for candidate in sorted(out): print(candidate)
