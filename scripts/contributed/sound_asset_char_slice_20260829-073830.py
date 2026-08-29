"""Bounded interior-character substitutions for a deterministic sound-asset seed slice.

The library-wide substitution generator materializes nearly a billion candidates before writing
them. This version keeps the same in-place transformation but limits it to the first 2,000
verified seeds and emits candidates directly, making a measured slice practical on both games.
"""
import argparse
import glob
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True, choices=("BLKOPSCW", "BLKOPS04"))
    ap.add_argument("--limit", type=int, default=2000)
    args = ap.parse_args()
    needle = args.game.lower()
    snap = next(snapshot.read(p) for p in snapshot.snapshots() if needle in os.path.basename(p).lower())
    pool_name = "sound_asset"
    wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == pool_name}
    hasher = snapshot.fnv1a_nofold if args.game == "BLKOPS04" else snapshot.fnv1a
    names = []
    for path in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                name = name.strip()
                if name and hasher(name) & snapshot.ID_MASK in wanted:
                    names.append(name.lower().replace("\\", "/"))
    for path in glob.glob(os.path.join(ROOT, "findings", needle, "sound_asset.txt")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                if name.strip():
                    names.append(name.strip().lower().replace("\\", "/"))
    names = sorted(set(names))[:args.limit]
    alphabet = "_0123456789abcdefghijklmnopqrstuvwxyz"
    emitted = 0
    for name in names:
        cut = max(name.rfind("/"), name.rfind("\\")) + 1
        head, base = name[:cut], name[cut:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        for i, old in enumerate(core[:-4]):
            for char in alphabet:
                if char != old:
                    print(head + core[:i] + char + core[i + 1:] + tail)
                    emitted += 1
    print("sound asset char slice: %d seeds, %d candidates" % (len(names), emitted), file=sys.stderr)


if __name__ == "__main__":
    main()
