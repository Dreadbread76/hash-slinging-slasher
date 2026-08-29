"""Probe high-frequency sound-alias beginnings that the measured prefix list does not carry."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGINNINGS = (
    "bik_execution_", "grp_", "cac_wildcard_equip_", "duk_",
    "phy_impact_hard_", "phy_impact_metal_", "phy_impact_soft_", "chr_gib_",
    "vox_", "amb_", "foley_", "npc_", "weap_", "ui_", "streak_", "radio_",
)

def main():
    suffixes = [x.strip().lower().replace("\\", "/")
                for x in (ROOT / "data" / "sound.suffixes.txt").read_text().splitlines()
                if x.strip()]
    out = {begin + suffix.lstrip("_") for begin in BEGINNINGS for suffix in suffixes}
    for value in sorted(out):
        print(value)
    print(f"{len(BEGINNINGS)} uncarried sound beginnings x {len(suffixes)} measured suffixes = {len(out)} candidates", file=__import__("sys").stderr)

if __name__ == "__main__":
    main()
