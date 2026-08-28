"""Wear newly recovered xmodel attachment cores with measured material decorations."""
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import seams

NEW_XMODELS = (
    "attach_t8_lmg_hades_dbal_1_view",
    "attach_t8_lmg_hades_dbal_1_world",
    "attach_t8_lmg_hades_dbal_2_view",
    "attach_t8_lmg_hades_dbal_2_world",
    "attach_t8_sniper_vanguard_barrel_1_sig_02_view",
    "attach_t8_sniper_vanguard_barrel_1_sig_02_world",
    "attach_t8_sniper_vanguard_barrel_2_sig_02_view",
    "attach_t8_sniper_vanguard_barrel_2_sig_02_world",
)


def decorations(names):
    heads, tails = Counter(), Counter()
    for name in names:
        directory, bare = seams.split_directory(name)
        parts = bare.split("_")
        if len(parts) > 2:
            heads[directory + parts[0] + "_"] += 1
            tails["_" + parts[-1]] += 1
    return [x for x, _ in heads.most_common(24)], [x for x, _ in tails.most_common(24)]


def main():
    material = seams.load("material")
    heads, tails = decorations(material)
    cores = sorted({x.rsplit("_", 1)[0] for x in NEW_XMODELS})
    count = 0
    for core in cores:
        for head in heads:
            for tail in tails:
                print(head + core + tail)
                count += 1
    print(f"{count:,} streamed xmodel-to-material snowball candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
