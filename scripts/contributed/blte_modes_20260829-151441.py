"""Census of BLTE chunk modes across a build's archives -- what is readable and what is not.

    python contrib/blte_modes.py                  Black Ops 4
    python contrib/blte_modes.py --game BLKOPSCW

METHODS *17. What is left of this* records the last open question about the build:

> **Encrypted frames.** BLTE mode `E` is Salsa20 against the build's key ring, and mode `F` is a
> recursive frame. Both are dropped rather than guessed at. **Neither has been counted.**

This counts them. It reads only the frame headers and the one mode byte in front of each chunk,
never a payload, so it is minutes rather than hours.

Modes: `N` stored, `Z` zlib, `4` LZ4, `F` a recursive BLTE frame, `E` Salsa20 against the key ring.
"""

import argparse
import collections
import glob
import os
import struct
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "contrib"))

ROOTS = {
    "BLKOPS04": r"D:\Battlenet\Call of Duty Black Ops 4",
    "BLKOPSCW": r"D:\Battlenet\Call of Duty Black Ops Cold War",
}
HEADER = 30


def frames(folder):
    """(archive, offset, size) for every real frame, straight from the CASC index."""
    for path in sorted(glob.glob(os.path.join(folder, "*.idx"))):
        with open(path, "rb") as handle:
            blob = handle.read()
        (hash_size,) = struct.unpack_from("<I", blob, 0)
        version, _b, _e, size_len, offset_len, key_len, offset_bits = \
            struct.unpack_from("<HBBBBBB", blob, 8)
        if version != 7:
            continue
        base = (8 + hash_size + 0x0F) & ~0x0F
        (entries_size,) = struct.unpack_from("<I", blob, base)
        at, stride = base + 8, key_len + offset_len + size_len
        mask = (1 << offset_bits) - 1
        for i in range(entries_size // stride):
            rec = at + i * stride
            packed = int.from_bytes(blob[rec + key_len:rec + key_len + offset_len], "big")
            size = int.from_bytes(blob[rec + key_len + offset_len:rec + key_len + offset_len + size_len], "little")
            if size > HEADER:
                yield packed >> offset_bits, packed & mask, size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", default="BLKOPS04", choices=sorted(ROOTS))
    args = parser.parse_args()
    folder = os.path.join(ROOTS[args.game], "Data", "data")
    if not os.path.isdir(folder):
        raise SystemExit("no build at %s" % folder)

    modes = collections.Counter()
    mode_bytes = collections.Counter()
    frames_with = collections.defaultdict(set)
    single = bad = total = 0

    handles = {}
    for archive, offset, size in frames(folder):
        path = os.path.join(folder, "data.%03d" % archive)
        if not os.path.exists(path):
            continue
        handle = handles.get(archive) or handles.setdefault(archive, open(path, "rb"))
        total += 1
        handle.seek(offset + HEADER)
        head = handle.read(8)
        if len(head) < 8 or head[:4] != b"BLTE":
            bad += 1
            continue
        (header_size,) = struct.unpack(">I", head[4:8])

        if header_size == 0:                       # one chunk, data starts immediately
            mode = handle.read(1)
            single += 1
            if mode:
                modes[mode.decode("latin-1")] += 1
                mode_bytes[mode.decode("latin-1")] += size
                frames_with[mode.decode("latin-1")].add((archive, offset))
            continue

        table = handle.read(header_size - 8)
        if len(table) < 4:
            bad += 1
            continue
        count = int.from_bytes(table[1:4], "big")
        at = offset + HEADER + header_size
        for i in range(count):
            entry = 4 + i * 24
            if entry + 8 > len(table):
                break
            (comp,) = struct.unpack_from(">I", table, entry)
            handle.seek(at)
            mode = handle.read(1)
            at += comp
            if mode:
                key = mode.decode("latin-1")
                modes[key] += 1
                mode_bytes[key] += comp
                frames_with[key].add((archive, offset))

    for handle in handles.values():
        handle.close()

    print("%s: %d frames (%d single-chunk), %d unreadable" % (args.game, total, single, bad))
    print("%d chunks\n" % sum(modes.values()))
    print("%-6s %12s %14s %10s" % ("mode", "chunks", "bytes", "frames"))
    for key, n in modes.most_common():
        print("%-6s %12d %13.1fG %10d" % (key, n, mode_bytes[key] / 1e9, len(frames_with[key])))


if __name__ == "__main__":
    main()
