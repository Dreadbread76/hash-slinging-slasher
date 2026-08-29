"""Emit names formed by deleting two distinct basename characters from known Cold War names.

This probes zero-padding and other two-character spelling changes that one-character edits cannot
reach.  Directory components are preserved; only the basename is edited.
"""
import argparse, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = {
    "model": "fnv1a_xmodels", "material": "fnv1a_xmaterials",
    "image": "fnv1a_ximages", "anim": "fnv1a_xanims",
}

def names(kind):
    vals = list(snapshot.table_names(TABLES[kind])) + list(snapshot.confirmed_names({
        "model": "xmodel", "material": "material", "image": "image", "anim": "xanim"
    }[kind]))
    return {x.strip().lower().replace("\\", "/") for x in vals if x.strip()}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", action="append", choices=sorted(TABLES))
    ap.add_argument("--size", action="store_true")
    args = ap.parse_args()
    seen = set(); total = 0
    for kind in args.type or sorted(TABLES):
        count = 0
        for name in names(kind):
            cut = name.rfind("/") + 1
            head, base = name[:cut], name[cut:]
            for i in range(len(base)):
                for j in range(i + 1, len(base)):
                    candidate = head + base[:i] + base[i + 1:j] + base[j + 1:]
                    if not candidate or candidate in seen:
                        continue
                    seen.add(candidate); count += 1
                    if not args.size:
                        print(candidate)
        total += count
        print(f"{kind}: {count:,} candidates", file=sys.stderr)
    print(f"{total:,} candidates", file=sys.stderr)

if __name__ == "__main__":
    main()
