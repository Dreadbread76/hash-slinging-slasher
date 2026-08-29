"""Generate Black Ops 4 xanim names by replacing one token in a known animation.

This is deliberately xanim-only: each replacement is learned from the same token
position in another real xanim name, preserving the animation naming grammar while
reaching combinations no cross-pool pass can express.
"""
import pathlib, re, sys
from collections import defaultdict, Counter

ROOT = pathlib.Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

def main():
    names = set(snapshot.table_names("fnv1a_xanims", "fnv1a_xanims_v2"))
    names.update(snapshot.confirmed_names("xanim"))
    names = {n.strip().lower() for n in names if n.strip() and "_" in n}
    # Position-specific vocabularies avoid inventing arbitrary token grammar.
    vocab = defaultdict(Counter)
    parsed = []
    for n in names:
        p = n.split("_")
        # Keep the transition-shaped corpus: it is the measured xanim grammar
        # and avoids exploding on long generated animation names.
        if len(p) >= 4 and p[-3] == "to":
            parsed.append(p)
        for i, tok in enumerate(p):
            vocab[(len(p), i)][tok] += 1
    seen = set()
    # Keep the measured common vocabulary; this makes the pass finite and reproducible.
    top = {k: [t for t, _ in v.most_common(8)] for k, v in vocab.items()}
    for p in parsed:
        for i in range(len(p)):
            for tok in top[(len(p), i)]:
                if tok == p[i]:
                    continue
                q = p[:]
                q[i] = tok
                n = "_".join(q)
                if n not in seen:
                    seen.add(n)
                    print(n)

if __name__ == "__main__":
    main()
