"""Emit Cold War mcdp material redecorations from every known material core."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

known = {n.strip().lower().replace("\\", "/")
         for n in snapshot.table_names("fnv1a_xmaterials", "fnv1a_xmaterials_v2")
         if n.strip()}
known.update(n.strip().lower().replace("\\", "/")
            for n in snapshot.confirmed_names("material") if n.strip())

cores = set()
for name in known:
    if "/" not in name:
        continue
    core = name.split("/", 1)[1]
    if core.startswith("mtl_"):
        core = core[4:]
    if core:
        cores.add(core)

out = set()
for core in cores:
    for spelling in (core, "mtl_" + core):
        candidate = "mcdp/" + spelling
        if candidate not in known:
            out.add(candidate)

print(f"{len(cores):,} material cores, {len(out):,} candidates", file=sys.stderr)
for candidate in sorted(out):
    print(candidate)
