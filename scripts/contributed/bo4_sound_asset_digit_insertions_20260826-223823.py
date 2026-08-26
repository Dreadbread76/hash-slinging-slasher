"""Generate BO4 sound_asset names formed by inserting one measured digit in a known SAB basename.

The dotted encoding tail is preserved; BO4 sound paths remain backslash-spelled and are filtered
against the BO4 sound_asset pool before edits.  This is a bounded character-length seam distinct
from tail replacement and directory/basename recombination.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot


def main():
    snap = snapshot.read(str(ROOT / "snapshots" / "blkops04.ids"))
    wanted = {asset for asset, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
    names = set()
    for name in snapshot.confirmed_names("sound_asset"):
        if snapshot.fnv1a_nofold(name) in wanted:
            names.add(name.strip().lower())
    for name in snapshot.table_names("fnv1a_xsounds"):
        if snapshot.fnv1a_nofold(name) in wanted:
            names.add(name.strip().lower())

    seen = set()
    count = 0
    for name in sorted(names):
        dot = name.find(".")
        if dot <= 0:
            continue
        base, tail = name[:dot], name[dot:]
        # Preserve the directory and the SAB dotted tail; only edit the basename.
        cut = max(base.rfind("\\"), base.rfind("/")) + 1
        prefix, stem = base[:cut], base[cut:]
        for pos in range(len(stem) + 1):
            for digit in "0123456789":
                candidate = prefix + stem[:pos] + digit + stem[pos:] + tail
                if candidate not in seen:
                    seen.add(candidate)
                    count += 1
                    print(candidate)
    print(f"{len(names)} BO4 sound_asset seeds, {count} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
