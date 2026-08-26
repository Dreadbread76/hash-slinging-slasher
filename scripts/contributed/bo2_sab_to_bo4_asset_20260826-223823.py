"""Transfer BO2 SAB cores into BO4's literal-backslash sound_asset grammar."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
TAILS = ("ln100.pc.snd", "ll100.pc.snd", "sn100.pc.snd", "sl100.pc.snd", "pn100.pc.snd", "pl100.pc.snd")
LANG = {"en","ru","fr","de","it","es","pt","pl","ja","ko","zh","cz","ar"}
def main():
    seen = set()
    for line in (ROOT / "borrowed" / "bo2_sab.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        n = line.strip().lower().replace("/", "\\")
        core = n.split(".", 1)[0]
        if not core: continue
        parts = core.split("\\")
        if parts and parts[0] in LANG: parts = parts[1:]
        core = "\\".join(parts)
        if core: seen.add(core)
    for core in sorted(seen):
        for tail in TAILS: print(core + "." + tail)
    print(f"{len(seen)} BO2 cores, {len(seen)*len(TAILS)} candidates", file=__import__('sys').stderr)
if __name__ == "__main__": main()
