"""Build a BO4 sound_asset plan by replacing the final three base-path bytes."""
import argparse, collections, itertools, os, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=3)
    ap.add_argument("--plan", default=None)
    args = ap.parse_args()
    snap = snapshot.read(str(ROOT / "snapshots" / "blkops04.ids"))
    ids = {i for i, p in snap.records if snap.pool_name(p) == "sound_asset"}
    names = set(snapshot.confirmed_names("sound_asset"))
    for n in snapshot.table_names("fnv1a_xsounds", "fnv1a_xsounds_v2", "bo3_sab", "bo2_sab"):
        if snapshot.fnv1a_nofold(n) in ids:
            names.add(n)
    tails = collections.Counter()
    bases = set()
    for n in names:
        n = n.lower().replace("/", "\\")
        dot = n.rfind(".")
        if dot < 3:
            continue
        base, tail = n[:dot], n[dot:]
        if len(base) > args.length:
            bases.add(base[:-args.length])
        tails[tail] += 1
    alphabet = collections.Counter(ch for b in bases for ch in b[-4:])
    chars = [c for c, _ in alphabet.most_common(37)]
    endings = ["".join(x) + t for x in itertools.product(chars, repeat=args.length) for t, _ in tails.most_common(6)]
    stems = sorted(b for b in bases if len(b) >= 6)
    plan = ROOT / "plans" / (args.plan or f"bo4_sound_asset_base_tail{args.length}_20260826.txt")
    sf, ef = ROOT / "contrib" / "bo4_sound_asset_base_tail3.stems.txt", ROOT / "contrib" / "bo4_sound_asset_base_tail3.endings.txt"
    sf.write_text("\n".join(stems) + "\n", encoding="utf-8")
    ef.write_text("\n".join(endings) + "\n", encoding="utf-8")
    plan.write_text(f"label: BO4 sound_asset confirmed base tail-{args.length} variants\n"+
                    "describe: confirmed SAB base paths with final three base bytes replaced; unfolded\n"+
                    f"stem: @contrib/{sf.name}\nend: @contrib/{ef.name}\nbare: yes\nfold: no\n", encoding="utf-8")
    print(f"{len(names)} sound_asset seeds, {len(stems)} stems, {len(endings)} endings, {len(stems)*len(endings)} candidates")

if __name__ == "__main__": main()
