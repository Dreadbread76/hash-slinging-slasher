"""Interior character substitutions on confirmed CW sound_asset names only."""
import glob, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot
def main():
    snap = next(snapshot.read(p) for p in snapshot.snapshots() if "blkopscw" in os.path.basename(p).lower())
    wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
    names = []
    for path in glob.glob("cod-name-db/csv/*xsounds*.csv"):
        for line in open(path, encoding="utf-8", errors="replace"):
            _, _, name = line.partition(","); name = name.strip()
            if name and snapshot.fnv1a(name) & snapshot.ID_MASK in wanted: names.append(name)
    for path in glob.glob("findings/blkopscw/sound_asset.txt"):
        for line in open(path, encoding="utf-8", errors="replace"):
            comma = line.find(",")
            if comma >= 0: names.append(line[comma + 1:].rstrip("\r\n"))
    names = sorted(set(names)); counts = {}
    for n in names:
        for c in n: counts[c] = counts.get(c, 0) + 1
    total = sum(counts.values()) or 1
    alphabet = sorted(c for c, n in counts.items() if n / total >= .0002 and c not in "\\/*.")
    seen = set()
    for n in names:
        cut = max(n.rfind("/"), n.rfind("\\")) + 1; head, base = n[:cut], n[cut:]
        dot = base.find(".")
        if dot <= 0: continue
        core, tail = base[:dot], base[dot:]
        for i, old in enumerate(core):
            for c in alphabet:
                if c != old:
                    seen.add(head + core[:i] + c + core[i + 1:] + tail)
    for c in sorted(seen): print(c)
    print(f"{len(names)} seeds, {len(seen)} candidates", file=sys.stderr)
if __name__ == "__main__": main()
