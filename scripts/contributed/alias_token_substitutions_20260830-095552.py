"""Replace sound-alias tokens with frequent alternatives at the same position."""
import collections
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

known = {
    n.strip().lower().replace("\\", "/")
    for n in list(snapshot.table_names("fnv1a_soundbanks_aliases"))
    + list(snapshot.confirmed_names("sound_alias"))
    if n.strip()
}
parsed = [n.split("_") for n in known if 2 <= len(n.split("_")) <= 12]
vocab = collections.defaultdict(collections.Counter)
for tokens in parsed:
    for pos, token in enumerate(tokens):
        vocab[(tokens[0], pos)][token] += 1
alternatives = {
    key: [word for word, count in counts.most_common(20) if count >= 2]
    for key, counts in vocab.items()
}

seen = set()
for tokens in parsed:
    for pos, old in enumerate(tokens):
        for word in alternatives.get((tokens[0], pos), ()):
            if word == old:
                continue
            candidate = "_".join(tokens[:pos] + [word] + tokens[pos + 1:])
            if candidate not in known and candidate not in seen:
                seen.add(candidate)
                print(candidate)

print(f"{len(seen):,} candidates", file=sys.stderr)
