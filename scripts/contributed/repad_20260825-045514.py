r"""The same name with a number written to a different width: `_01` <-> `_1` <-> `_001`.

    python contrib/repad.py | bin/windows/confirm_list.exe - \
        --label "numeric repadding" --script contrib/repad.py

## Why this and not `confirm_variants`

`confirm_variants` moves a number *in place* -- `_01` to `_02`, `_02` to `_03` -- and
`families.py --gaps` fills the holes in a numbered run. Both keep the number's **width** fixed,
because both were built to walk an axis, and an axis has a fixed format. Nothing here changes the
format itself, and the games are not consistent about it:

    mc/mtl_p9_yagor_bridge_center_console_decal_02   and   ..._decal_002
    p9_fxanim_cp_armada_rocket_cave_017             and   ..._cave_17
    i_mtl_air_duct02_n                              and   i_mtl_air_duct2_n

Measured over 400,001 digit-carrying names on 2026-08-25: **91 have a differently-padded sibling
already in the corpus, 1 per 4,396.** That is a real convention -- better than `token_order`'s
1 per 7,700 -- and it is a *narrow* one, which is the honest reading: padding is overwhelmingly
stable, so this is a cheap sweep and not a night's work. It is here because it costs about ten
seconds of machine and because it composes: every name it recovers is a fresh stem for everything
in `derive_closure`.

Each numeric run in a name is re-emitted at widths 1 to 4, one run at a time, so a candidate is
never more than one edit from a name known to be real -- the shape METHODS records as live.
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import snapshot  # noqa: E402

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims",
          "fnv1a_soundbanks_aliases")
RUN = re.compile(r"(?<![0-9])([0-9]+)(?![0-9])")


def main():
    names = set(snapshot.table_names(*TABLES))
    names |= {n.strip() for n in snapshot.confirmed_names() if n.strip()}
    names = {n.lower() for n in names if n}
    sys.stderr.write("corpus: %s\n" % "{:,}".format(len(names)))

    seen = set()
    emitted = 0
    for name in names:
        if not any(c.isdigit() for c in name):
            continue
        for match in RUN.finditer(name):
            digits = match.group(1)
            value = digits.lstrip("0") or "0"
            if len(value) > 4:
                continue
            for width in (1, 2, 3, 4):
                padded = value.zfill(width)
                if padded == digits:
                    continue
                candidate = name[:match.start()] + padded + name[match.end():]
                if candidate in names or candidate in seen:
                    continue
                seen.add(candidate)
                print(candidate)
                emitted += 1
    sys.stderr.write("candidates: %s\n" % "{:,}".format(emitted))


if __name__ == "__main__":
    main()
