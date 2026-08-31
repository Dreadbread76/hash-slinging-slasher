"""Generate sound aliases by incrementing or decrementing observed numeric tokens."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

known = {
    n.strip().lower().replace("\\", "/")
    for n in list(snapshot.table_names("fnv1a_soundbanks_aliases"))
    + list(snapshot.confirmed_names("sound_alias"))
    if n.strip()
}
seen = set()
for name in known:
    tokens = name.split("_")
    for pos, token in enumerate(tokens):
        if not token.isdigit():
            continue
        width = len(token)
        value = int(token)
        for neighbor in (value - 1, value + 1):
            if neighbor < 0 or neighbor >= 10 ** width:
                continue
            replacement = str(neighbor).zfill(width)
            changed = tokens[:]
            changed[pos] = replacement
            candidate = "_".join(changed)
            if candidate not in known and candidate not in seen:
                seen.add(candidate)
                print(candidate)

print(f"{len(seen):,} candidates", file=sys.stderr)
