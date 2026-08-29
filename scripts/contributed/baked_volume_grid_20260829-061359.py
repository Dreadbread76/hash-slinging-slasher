"""The lighting bake's own grid: `volume<V>_state<S>_<kind>_<map>_<index>`.

    python contrib/baked_volume_grid.py            every cell the bake would have emitted
    python contrib/baked_volume_grid.py --measure  the density measurement, and stop

## Why this shape, when every other grid here is dead

Four grids are recorded dead in METHODS.md -- the animation transition grid, the `vox_`
slot grid, the cosmetic-bundle grid, and materials through the thirteenth directory. Each
returned 0, and the dead ends draw one conclusion from them: *a store shipped the cells it
shipped*. An unobserved cell in an authored grid is unobserved because nobody made it.

Every one of those grids is **authored**. This one is not. These names are emitted by the
lighting bake, once per map, and a compiler that writes cell 41 and cell 43 wrote cell 42.
That is the whole argument for building it, and it is measurable before a single candidate
is hashed:

    380 observed (map, volume, state, kind) groups
    288 of them -- 76% -- have a completely contiguous index run 0..max

An authored grid does not do that. The 24% that do have holes are the reason to run it:
inside the spans already observed there are 18,350 missing indices, and each one is a name
the bake must have written and the tables do not hold.

## What it emits

Three bands, cheapest and best-evidenced first:

  gaps     missing indices inside an observed run. Strongest: both neighbours are published.
  extend   past the observed maximum of a run, by a margin -- the tables need not have
           caught the tail of any run.
  cross    (volume, state, kind) combinations never observed for a map that is observed,
           over that map's own index range. Weakest band, and the one that tests whether
           the grid is really a cross product or just a set of runs.

The map id is an 8 hex digit stamp and is *not* guessable, so only the 31 already published
are used. That is the ceiling on this method and it is worth stating: it cannot reach a map
nobody has named a single asset of.
"""

import argparse
import collections
import glob
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent

PATTERN = re.compile(r"^volume(\d+)_state(\d+)_(.+?)_([0-9a-f]{8})_([0-9a-f]+)$")


def published():
    """Every `volume...` name any published table holds, parsed into its five fields."""
    rows, seen = [], set()
    for path in glob.glob(str(ROOT / "cod-name-db" / "csv" / "*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.strip().partition(",")
                if not name.startswith("volume"):
                    continue
                name = name.strip().lower()
                if name in seen:
                    continue
                seen.add(name)
                match = PATTERN.match(name)
                if match:
                    rows.append(match.groups())
    return rows, seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--measure", action="store_true", help="print the density and stop")
    parser.add_argument("--margin", type=int, default=64,
                        help="how far past an observed run's maximum to extend")
    args = parser.parse_args()

    rows, seen = published()
    groups = collections.defaultdict(set)
    for volume, state, kind, stamp, index in rows:
        groups[(stamp, volume, state, kind)].add(int(index, 16))

    volumes = sorted({r[0] for r in rows}, key=int)
    states = sorted({r[1] for r in rows}, key=int)
    kinds = sorted({r[2] for r in rows})
    stamps = sorted({r[3] for r in rows})

    # Per map, the widest index run seen under any of its groups. A bake numbers a map's
    # probes by how many the map has, so the range travels with the map, not the volume.
    reach = collections.defaultdict(int)
    for (stamp, _, _, _), idxs in groups.items():
        reach[stamp] = max(reach[stamp], max(idxs))

    if args.measure:
        full = sum(1 for i in groups.values() if len(i) == max(i) + 1)
        holes = sum(max(i) + 1 - len(i) for i in groups.values())
        print(f"{len(seen):,} published volume names, {len(rows):,} parsed")
        print(f"{len(groups)} groups over {len(stamps)} maps; "
              f"{len(volumes)} volumes, {len(states)} states, {len(kinds)} kinds")
        print(f"contiguous runs: {full}/{len(groups)} ({full/len(groups):.0%})")
        print(f"missing indices inside observed runs: {holes:,}")
        return

    out = []
    for (stamp, volume, state, kind), idxs in groups.items():
        top = max(idxs)
        for i in range(top + 1):                       # band 1: gaps
            if i not in idxs:
                out.append(f"volume{volume}_state{state}_{kind}_{stamp}_{i:x}")
        for i in range(top + 1, top + 1 + args.margin):  # band 2: extend
            out.append(f"volume{volume}_state{state}_{kind}_{stamp}_{i:x}")

    for stamp in stamps:                                # band 3: cross
        top = reach[stamp]
        for volume in volumes:
            for state in states:
                for kind in kinds:
                    if (stamp, volume, state, kind) in groups:
                        continue
                    for i in range(top + 1):
                        out.append(f"volume{volume}_state{state}_{kind}_{stamp}_{i:x}")

    emitted = 0
    for name in out:
        if name not in seen:
            print(name)
            emitted += 1
    print(f"{emitted:,} candidates from {len(groups)} observed groups", file=sys.stderr)


if __name__ == "__main__":
    main()
