"""Try a disjoint measured xmodel tail band on the newly recovered attachment bodies."""
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


def main():
    xmodel = seams.load("xmodel")
    heads, tails = Counter(), Counter()
    for name in xmodel:
        directory, bare = seams.split_directory(name)
        parts = bare.split("_")
        if len(parts) > 2:
            heads[directory + parts[0] + "_"] += 1
            tails["_" + parts[-1]] += 1
    beginnings = [x for x, _ in heads.most_common(10)]
    endings = [x for x, _ in tails.most_common(30)[10:]]
    count = 0
    for core in CORES:
        for beginning in beginnings:
            for ending in endings:
                print(beginning + core + ending)
                count += 1
    print(f"{count:,} streamed attachment rare xmodel-tail candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
