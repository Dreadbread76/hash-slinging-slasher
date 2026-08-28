"""Wear newly recovered attachment bodies with measured image decorations."""
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import seams

CORES = (
    "attach_t8_lmg_hades_dbal_1", "attach_t8_lmg_hades_dbal_2",
    "attach_t8_sniper_vanguard_barrel_1_sig_02", "attach_t8_sniper_vanguard_barrel_2_sig_02",
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
    image = seams.load("image")
    heads, tails = decorations(image)
    count = 0
    for core in CORES:
        for head in heads:
            for tail in tails:
                print(head + core + tail)
                count += 1
    print(f"{count:,} streamed xmodel-to-image snowball candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
