"""Swap each adjacent pair inside confirmed sound-asset basenames."""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def names():
    snap = snapshot.read(next(p for p in snapshot.snapshots()
                              if "blkops04" in os.path.basename(p).lower()))
    wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
    result = set()
    for path in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, value = line.partition(",")
                value = value.strip()
                if value and snapshot.fnv1a_nofold(value) & snapshot.ID_MASK in wanted:
                    result.add(value.lower().replace("/", "\\"))
    with open(os.path.join(ROOT, "findings", "blkops04", "sound_asset.txt"), encoding="utf-8", errors="replace") as handle:
        for line in handle:
            _, sep, value = line.partition(",")
            if sep and value.strip():
                result.add(value.strip().lower().replace("/", "\\"))
    return sorted(result)


def main():
    seeds = names()
    output = set()
    for value in seeds:
        cut = max(value.rfind("\\"), value.rfind("/")) + 1
        head, base = value[:cut], value[cut:]
        dot = base.find(".")
        if dot <= 1:
            continue
        core, tail = base[:dot], base[dot:]
        for index in range(len(core) - 1):
            if core[index] == core[index + 1]:
                continue
            swapped = core[:index] + core[index + 1] + core[index] + core[index + 2:]
            output.add(head + swapped + tail)
    print(f"{len(seeds):,} seeds -> {len(output):,} adjacent-swap candidates", file=sys.stderr)
    print("\n".join(sorted(output)))


if __name__ == "__main__":
    main()
