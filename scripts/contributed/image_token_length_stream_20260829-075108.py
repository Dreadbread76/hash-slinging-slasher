"""Stream image names one token longer or shorter than an attested image name.

This is the image-only, streaming form of token_edits: it preserves the measured per-head
insertion vocabulary but avoids buffering the full candidate set in Python memory.
"""
import collections
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = ("fnv1a_ximages", "fnv1a_ximages_v2")
MAX_TOKENS = 12
CAP = 12
MIN_SEEN = 8


def split(name):
    directory, _, base = name.rpartition("/")
    return (directory + "/" if directory else ""), base.split("_")


def main():
    known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES)}
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names("image"))
    known.discard("")
    parsed = [(split(name), name) for name in known]
    seen_words = collections.defaultdict(collections.Counter)
    for (directory, tokens), _ in parsed:
        if len(tokens) <= MAX_TOKENS:
            for pos, token in enumerate(tokens):
                seen_words[(tokens[0], pos)][token] += 1
    words = {key: [word for word, count in counter.most_common(CAP) if count >= MIN_SEEN]
             for key, counter in seen_words.items()}
    emitted = 0
    for (directory, tokens), name in parsed:
        if not (1 < len(tokens) <= MAX_TOKENS):
            continue
        for pos in range(len(tokens)):
            candidate = directory + "_".join(tokens[:pos] + tokens[pos + 1:])
            if candidate and candidate not in known:
                print(candidate)
                emitted += 1
        head = tokens[0]
        for pos in range(1, len(tokens) + 1):
            for word in words.get((head, min(pos, len(tokens) - 1)), ()):
                candidate = directory + "_".join(tokens[:pos] + [word] + tokens[pos:])
                if candidate not in known:
                    print(candidate)
                    emitted += 1
    print("image token length stream: %d seeds, %d candidates" % (len(parsed), emitted), file=sys.stderr)


if __name__ == "__main__":
    main()
