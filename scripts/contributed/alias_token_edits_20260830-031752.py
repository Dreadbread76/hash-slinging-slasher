"""Seeded token insertion/deletion for sound-alias names."""
import collections
import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
while root != os.path.dirname(root) and not os.path.isfile(os.path.join(root, "scripts", "snapshot.py")):
    root = os.path.dirname(root)
sys.path.insert(0, os.path.join(root, "scripts"))
import snapshot

known = {
    n.strip().lower().replace("\\", "/")
    for n in list(snapshot.table_names("fnv1a_soundbanks_aliases"))
    + list(snapshot.confirmed_names("sound_alias"))
    if n.strip()
}
parsed = [(n.split("_")) for n in known if len(n.split("_")) >= 2 and len(n.split("_")) <= 12]
vocab = collections.defaultdict(collections.Counter)
for tokens in parsed:
    for pos, token in enumerate(tokens):
        vocab[(tokens[0], pos)][token] += 1

words = {key: [word for word, count in counts.most_common(20) if count >= 2]
         for key, counts in vocab.items()}
seen = set()
counting = "--count" in sys.argv
for tokens in parsed:
    for pos in range(len(tokens)):
        candidate = "_".join(tokens[:pos] + tokens[pos + 1:])
        if candidate not in known and candidate not in seen:
            seen.add(candidate)
            if not counting:
                print(candidate)
    for pos in range(1, len(tokens) + 1):
        for word in words.get((tokens[0], min(pos, len(tokens) - 1)), ()):
            candidate = "_".join(tokens[:pos] + [word] + tokens[pos:])
            if candidate not in known and candidate not in seen:
                seen.add(candidate)
                if not counting:
                    print(candidate)
if counting:
    print(len(seen), file=sys.stderr)
