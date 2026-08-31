"""Bounded interior-character substitutions for a deterministic sound-asset seed slice."""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

GAME = sys.argv[sys.argv.index("--game") + 1] if "--game" in sys.argv else "BLKOPSCW"
SEED_LIMIT = 2000
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz_-"

def main():
    snap = snapshot.read(os.path.join(ROOT, "snapshots", GAME.lower() + ".ids"))
    wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
    names = set()
    for table in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
        with open(table, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                name = name.strip()
                if name and snapshot.fnv1a(name) & snapshot.ID_MASK in wanted:
                    names.add(name)
    names.update(snapshot.confirmed_names("sound_asset"))
    seeds = sorted(n.strip() for n in names if n.strip())[:SEED_LIMIT]
    count = 0
    for name in seeds:
        cut = max(name.rfind("/"), name.rfind("\\")) + 1
        head, base = name[:cut], name[cut:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        for index, old in enumerate(core):
            for char in ALPHABET:
                if char != old:
                    print(head + core[:index] + char + core[index + 1:] + tail)
                    count += 1
    print(f"{GAME}: {len(seeds)} bounded seeds, {count} candidates", file=sys.stderr)

if __name__ == "__main__":
    main()
