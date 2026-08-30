"""Replace three sound-alias tokens with frequent positional alternatives."""
import collections
import itertools
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
parsed = [n.split("_") for n in known if 4 <= len(n.split("_")) <= 12]
vocab = collections.defaultdict(collections.Counter)
for tokens in parsed:
    for pos, token in enumerate(tokens):
        vocab[(tokens[0], pos)][token] += 1
alternatives = {
    key: [word for word, count in counts.most_common(3) if count >= 2]
    for key, counts in vocab.items()
}

seen = set()
for tokens in parsed:
    for positions in itertools.combinations(range(len(tokens)), 3):
        choices = []
        for pos in positions:
            choices.append([w for w in alternatives.get((tokens[0], pos), ()) if w != tokens[pos]])
        for replacement in itertools.product(*choices):
            changed = tokens[:]
            for pos, word in zip(positions, replacement):
                changed[pos] = word
            candidate = "_".join(changed)
            if candidate not in known and candidate not in seen:
                seen.add(candidate)
                print(candidate)

print(f"{len(seen):,} candidates", file=sys.stderr)
