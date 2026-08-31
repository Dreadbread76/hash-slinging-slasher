"""Swap adjacent underscore tokens in confirmed sound-alias names."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def main():
    known = {n.strip().lower() for n in snapshot.table_names("fnv1a_soundbanks_aliases") if n.strip()}
    known.update(n.strip().lower() for n in snapshot.confirmed_names("sound_alias") if n.strip())
    output = set()
    for name in known:
        head, sep, body = name.rpartition("/")
        prefix = head + sep if sep else ""
        parts = body.split("_")
        for index in range(len(parts) - 1):
            if not parts[index] or not parts[index + 1]:
                continue
            swapped = parts[:]
            swapped[index], swapped[index + 1] = swapped[index + 1], swapped[index]
            candidate = prefix + "_".join(swapped)
            if candidate not in known:
                output.add(candidate)
    print(f"{len(known):,} sound-alias seeds -> {len(output):,} adjacent-token candidates", file=sys.stderr)
    print("\n".join(sorted(output)))


if __name__ == "__main__":
    main()
