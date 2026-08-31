#!/usr/bin/env python3
"""Hex-indexed grid completion over the GI volume and reflection-probe image families.

## Why this reaches ground nothing else does

Every gap filler in this repository enumerates a family's index in **decimal**. Measured over
the 3.54 M name corpus, 1,143 families carry a two-character index containing an `a`-`f`
digit -- 15,876 observed names a decimal enumerator could never have produced. They are not
scattered: they are almost entirely the lightmap/GI volume textures and reflection probes,
which are indexed in hex 00-ff. A decimal sweep reaches 100 of those 256 cells and cannot
express the other 156, whatever else it does right.

`reach.py --missing` reached the same place from the other side, and nobody had acted on it:
`volume14_state0_reflection_probes_f788ac97_` is listed as a beginning **no cut of which is
carried**, 104 names.

## The shape

    volume<V>_state<S>_<kind>_<blob8>_<index>

measured over the 42,558 published names beginning `volume`:

| axis | observed |
|---|---|
| V | 0 1 2 3 7 8 10 11 13 14 15 16 17 18 -- **4 5 6 9 12 never appear** |
| S | 0 1 2 3 |
| kind | gi_xyz_texture_mip0/1/2, reflection_probes |
| blob8 | 31 distinct |
| index | 240 of the 256 two-hex values, plus one-hex forms |

The missing volume numbers are the tell. A volume index that runs 0..18 with five holes is a
build artefact, not a design -- the holes are levels whose names were never published, and
they cost nothing to ask about.

This emits the full product, which is under three million candidates: free, and the whole
point is that it is cheap enough not to need pruning.
"""
import glob
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def corpus():
    """Every name this machine holds: the published tables and everything confirmed."""
    names = set()
    pats = [
        os.path.join(REPO, "cod-name-db", "csv", "*.csv"),
        os.path.join(REPO, "all_names", "*", "*.txt"),
    ]
    for pat in pats:
        for path in glob.glob(pat):
            try:
                with open(path, encoding="utf-8", errors="replace") as handle:
                    for line in handle:
                        line = line.strip()
                        if not line:
                            continue
                        if "," in line:
                            line = line.split(",", 1)[1].strip()
                        names.add(line.lower())
            except OSError:
                continue
    return names


SHAPE = re.compile(
    r"^volume(?P<v>\d+)_state(?P<s>\d+)_(?P<kind>.+?)_(?P<blob>[0-9a-f]{8})_(?P<idx>[0-9a-f]{1,2})$"
)


def main():
    names = corpus()

    volumes, states, kinds, blobs = set(), set(), set(), set()
    for name in names:
        m = SHAPE.match(name)
        if not m:
            continue
        volumes.add(int(m.group("v")))
        states.add(int(m.group("s")))
        kinds.add(m.group("kind"))
        blobs.add(m.group("blob"))

    if not blobs:
        print("no volume-family names in the corpus", file=sys.stderr)
        return

    # Close the holes in the volume axis rather than reproducing them, and allow a little
    # headroom past the largest observed. Same for state.
    volumes = range(0, max(volumes) + 3)
    states = range(0, max(states) + 2)

    # Mip levels are enumerated rather than taken verbatim: the corpus shows 0-2, and a
    # deeper chain is exactly the sort of thing that is present and unpublished.
    kinds = set(kinds) | {f"gi_xyz_texture_mip{n}" for n in range(6)}

    indices = [f"{n:02x}" for n in range(256)] + [f"{n:x}" for n in range(16)]

    emitted = 0
    out = sys.stdout
    for blob in sorted(blobs):
        for vol in volumes:
            for state in states:
                for kind in sorted(kinds):
                    head = f"volume{vol}_state{state}_{kind}_{blob}_"
                    for idx in indices:
                        candidate = head + idx
                        if candidate in names:
                            continue
                        out.write(candidate)
                        out.write("\n")
                        emitted += 1
    print(f"emitted {emitted} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
