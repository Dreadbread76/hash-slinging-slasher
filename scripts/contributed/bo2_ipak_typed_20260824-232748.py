"""bo2_ipak as a TYPED image corpus for the typed cross (method 18).

`borrowed/bo2_ipak.txt` is 10,677 Black Ops 2 image-package names. METHODS.md
records it dead -- but dead *verbatim*, in the row that hashed

    bo2_ipak, cod_constants, cod_semantics, cod_techsets, fnv1a_strings,
    944,345 names: 0

and method 18 is precisely the finding that **verbatim is the wrong test**. The
`_v2` tables are recorded dead the same way -- "all eight, 1,175,524 names hashed
verbatim against 336,505 unnamed ids, zero" -- and typed they returned hundreds,
because nothing about the corpus changed, "only whether an image core was asked
to wear image decorations".

`bo2_ipak` has never been tried typed, and it is the cleanest typed corpus on the
disk: an ipak *is* an image package, so every row is an image with no
classification needed and no community content mixed in. Its structure is the
familiar one a generation earlier --

    p6_...                 the map prefix, one generation before p7_/p8_/p9_
    em_bg_wpn_attach_...   attachment emblem backgrounds
    mtl_..., hud_..., menu_..., veh_..., zm_...

-- so its cores are exactly the kind of thing Black Ops 4 and Cold War reuse.

Emits a `type,name` manifest on stdout for `scripts/typed_cross.py --source`.

    python contrib/bo2_ipak_typed.py > plans/bo2_ipak.manifest.csv
    python scripts/typed_cross.py --source plans/bo2_ipak.manifest.csv \
        --write-plans plans/bo2ipak
    bin\windows\confirm_plan.exe plans/bo2ipak.image.txt --size
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "borrowed", "bo2_ipak.txt")


def main():
    out = sys.stdout
    kept = dropped = 0
    with open(SRC, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            name = line.rstrip("\r\n").strip()
            if not name:
                continue
            # `*lightmap0_secondary` and friends are generated per-map images,
            # named from map content rather than from vocabulary. They are the
            # ipak equivalent of a streamkey and carry nothing transferable.
            if name.startswith("*"):
                dropped += 1
                continue
            kept += 1
            out.write("image,")
            out.write(name)
            out.write("\n")
    sys.stderr.write("bo2_ipak_typed: %d image rows (%d generated names dropped)\n"
                     % (kept, dropped))


if __name__ == "__main__":
    main()
