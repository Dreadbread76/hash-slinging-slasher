"""Build a BO4-prefix x Cold War-core plan.

BO4 has many leading cuts absent from data/prefixes.txt.  This deliberately crosses
those BO4-specific cuts with cores learned from the other title, testing a seam that
the same-title uncarried-beginning pass cannot reach.
"""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import seams
import snapshot

TABLES = ["fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages", "fnv1a_ximages_v2",
          "fnv1a_xmodels", "fnv1a_xanims", "fnv1a_xanims_v2"]

def reductions(name):
    name = name.strip().lower().replace("\\", "/")
    out = set()
    reductions_by_label = dict(seams.REDUCTIONS)
    for label in ("no head", "no ends", "no tail"):
        core = reductions_by_label[label](name)
        if len(core) >= 4:
            out.add(core)
    return out

def main():
    carried = {x.strip() for x in (ROOT / "data" / "prefixes.txt").read_text().splitlines() if x.strip()}
    bo4 = {x.strip().lower().replace("\\", "/") for x in snapshot.table_names(*TABLES) if x.strip()}
    counts = collections.Counter()
    for name in bo4:
        for i, ch in enumerate(name):
            if ch in "_/" and i < 40:
                counts[name[:i + 1]] += 1
    begins = [b for b, _ in sorted(((b, n) for b, n in counts.items() if b not in carried), key=lambda x: (-x[1], x[0]))[:200]]
    # Published tables are the cleanest cross-title source; use CW's non-sound tables.
    cw = snapshot.table_names(*TABLES)
    stems = sorted({core for name in cw for core in reductions(name)})[:100000]
    bp = ROOT / "contrib" / "bo4_cross_title_begins.txt"
    sp = ROOT / "contrib" / "bo4_cross_title_stems.txt"
    pp = ROOT / "plans" / "bo4_uncarried_begins_cross_title.txt"
    bp.write_text("\n".join(begins) + "\n")
    sp.write_text("\n".join(stems) + "\n")
    pp.write_text("label: BO4 uncarried beginnings over cross-title cores\n"
                  "describe: BO4 leading cuts absent from the committed list over published cores\n\n"
                  "begin: @contrib/bo4_cross_title_begins.txt\n\n"
                  "stem: @contrib/bo4_cross_title_stems.txt\n\n"
                  "end: @data/suffixes.txt\n\n"
                  "bare: no\nfold: yes\n")
    print(f"{len(begins)} beginnings, {len(stems)} cores, {len(begins)*len(stems)*4629:,} candidates", file=sys.stderr)
    print(pp)

if __name__ == "__main__":
    main()
