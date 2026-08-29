"""Interior character substitutions on confirmed BO4 sound_asset names only.

Keeps the literal backslash path and dotted encoding tail intact; intended for
confirm_list --game BLKOPS04 --no-fold.
"""
import glob, os, sys
_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot

def main():
    snap = next(snapshot.read(p) for p in snapshot.snapshots()
                if "blkops04" in os.path.basename(p).lower())
    wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
    names = []
    for path in glob.glob("cod-name-db/csv/*xsounds*.csv"):
        for line in open(path, encoding="utf-8", errors="replace"):
            _, _, name = line.partition(",")
            name = name.strip()
            if name and snapshot.fnv1a_nofold(name) & snapshot.ID_MASK in wanted:
                names.append(name)
    for path in glob.glob("findings/blkops04/sound_asset.txt"):
        for line in open(path, encoding="utf-8", errors="replace"):
            comma = line.find(",")
            if comma >= 0:
                names.append(line[comma + 1:].rstrip("\r\n"))
    names = sorted(set(names))
    counts = {}
    for name in names:
        for c in name:
            counts[c] = counts.get(c, 0) + 1
    total = sum(counts.values()) or 1
    alphabet = sorted(c for c, n in counts.items()
                      if n / total >= .0002 and c not in "\\/*.")
    seen = set()
    for name in names:
        cut = max(name.rfind("/"), name.rfind("\\")) + 1
        head, base = name[:cut], name[cut:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        for i, old in enumerate(core):
            for c in alphabet:
                if c == old:
                    continue
                candidate = head + core[:i] + c + core[i + 1:] + tail
                if candidate not in seen:
                    seen.add(candidate)
                    print(candidate)
    print(f"{len(names)} seeds, {len(seen)} candidates", file=sys.stderr)

if __name__ == "__main__":
    main()
