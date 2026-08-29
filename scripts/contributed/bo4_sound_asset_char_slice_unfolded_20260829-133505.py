"""Bounded interior-character variants of known BO4 SAB sound paths.

BO4 sound assets hash the original backslash spelling.  This deliberately keeps backslashes
through candidate construction and is separate from the folded Cold War character slice.
"""
import glob
import os
import sys
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=2000)
    args = parser.parse_args()
    snap_path = next(p for p in snapshot.snapshots() if "blkops04" in os.path.basename(p).lower())
    snap = snapshot.read(snap_path)
    wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
    hasher = snapshot.fnv1a_nofold

    names = set()
    for path in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, raw = line.partition(",")
                raw = raw.strip()
                if raw and hasher(raw) & snapshot.ID_MASK in wanted:
                    names.add(raw.lower().replace("/", "\\"))

    found = os.path.join(ROOT, "findings", "blkops04", "sound_asset.txt")
    if os.path.exists(found):
        with open(found, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, raw = line.partition(",")
                raw = raw.strip()
                if raw:
                    names.add(raw.lower().replace("/", "\\"))

    seeds = sorted(names)[args.offset:args.offset + args.limit]
    alphabet = "_0123456789abcdefghijklmnopqrstuvwxyz"
    emitted = 0
    for name in seeds:
        cut = max(name.rfind("\\"), name.rfind("/")) + 1
        head, base = name[:cut], name[cut:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        for pos, old in enumerate(core[:-4]):
            for char in alphabet:
                if char != old:
                    print(head + core[:pos] + char + core[pos + 1:] + tail)
                    emitted += 1
    print(f"BO4 unfolded sound character slice: {len(seeds)} seeds, {emitted} candidates",
          file=sys.stderr)


if __name__ == "__main__":
    main()
