"""Enumerate every CASC archive entry from `Data/data/*.idx`, instead of hunting magic bytes.

    python contrib/casc_index.py                    Black Ops 4, summarise coverage
    python contrib/casc_index.py --game BLKOPSCW    the other build
    python contrib/casc_index.py --list             one `archive offset size` row per frame

## Why this exists

METHODS *17. The build itself* walks the archives by **hunting for the BLTE magic**, and its
"What is left of this" listed the index as the obvious upgrade:

> The `.idx` files. `Data/data/*.idx` maps every content key to an archive, offset and size.
> Reading them replaces the magic hunt and reaches entries the hunt cannot see -- worth doing
> if the archive sweep's yield justifies it.

The sweep's yield does justify it -- BO4 source literals is the most efficient method in the
registry at 42 candidates per name -- so this reads the index and answers the question.

**The answer is no, and that is the point of keeping this.** The index lists 2,028 real frames
for Black Ops 4; the magic hunt already found 2,101. The hunt is not missing entries, so there
is no hidden tail of the build to harvest and nobody needs to spend a night writing this again.

## The format, which is standard CASC v7 and worth writing down once

    uint32 headerHashSize          0x10
    uint32 headerHashCheck
    uint16 version                 7
    uint8  bucketIndex             0..15, one per .idx file
    uint8  extraBytes
    uint8  encodedSizeLength       4
    uint8  storageOffsetLength     5
    uint8  encodingKeyLength       9
    uint8  fileOffsetBits          30
    uint64 segmentSize
    ... pad to a 0x10 boundary ...
    uint32 entriesSize
    uint32 entriesHash
    entry[] { key[9]; storageOffset[5] big endian; encodedSize[4] little endian }

`storageOffset` packs both numbers: the low `fileOffsetBits` are the offset within the archive
and the rest is the archive number, so 5 bytes and 30 bits gives `data.000` .. `data.1023` and
a 1 GB cap per archive.

Two things that will waste an hour if you do not know them:

  - **More than half the entries are markers, not content.** They have `encodedSize == 30` and
    all carry the same body. Real frames are `> 30`, and every one of them has `BLTE` at
    exactly +30 -- the 30 bytes in front are the entry header that carries the frame's own size.
  - **Sizes are little endian while the storage offset is big endian**, in the same record.
"""

import argparse
import collections
import glob
import os
import struct
import sys

ROOTS = {
    "BLKOPS04": r"D:\Battlenet\Call of Duty Black Ops 4",
    "BLKOPSCW": r"D:\Battlenet\Call of Duty Black Ops Cold War",
}

MARKER_SIZE = 30          # an index marker, not a frame
HEADER = 30               # bytes of entry header in front of every BLTE frame


def entries(folder):
    """Yield (archive, offset, encoded size) for every real frame the index lists."""
    for path in sorted(glob.glob(os.path.join(folder, "*.idx"))):
        with open(path, "rb") as handle:
            blob = handle.read()
        if len(blob) < 0x28:
            continue
        (hash_size,) = struct.unpack_from("<I", blob, 0)
        version, _bucket, _extra, size_len, offset_len, key_len, offset_bits = \
            struct.unpack_from("<HBBBBBB", blob, 8)
        if version != 7:
            print("%s is index version %d, and this reads 7" % (path, version), file=sys.stderr)
            continue

        base = (8 + hash_size + 0x0F) & ~0x0F
        (entries_size,) = struct.unpack_from("<I", blob, base)
        at = base + 8
        stride = key_len + offset_len + size_len
        mask = (1 << offset_bits) - 1

        for index in range(entries_size // stride):
            record = at + index * stride
            packed = int.from_bytes(blob[record + key_len:record + key_len + offset_len], "big")
            size = int.from_bytes(
                blob[record + key_len + offset_len:record + key_len + offset_len + size_len],
                "little")
            if size <= MARKER_SIZE:
                continue
            yield packed >> offset_bits, packed & mask, size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", default="BLKOPS04", choices=sorted(ROOTS))
    parser.add_argument("--list", action="store_true", help="print every frame, not a summary")
    parser.add_argument("--verify", type=int, default=0,
                        help="seek this many frames and check for BLTE at +30")
    args = parser.parse_args()

    folder = os.path.join(ROOTS[args.game], "Data", "data")
    if not os.path.isdir(folder):
        raise SystemExit("no build at %s" % folder)

    frames = list(entries(folder))
    if args.list:
        for archive, offset, size in frames:
            print("%d %d %d" % (archive, offset, size))
        return

    sizes = sorted(size for _, _, size in frames)
    per = collections.Counter(archive for archive, _, _ in frames)
    print("%s: %d frames across %d archives" % (args.game, len(frames), len(per)))
    print("  size min/median/max: %d / %d / %d" % (sizes[0], sizes[len(sizes) // 2], sizes[-1]))
    print("  framed bytes: %.1f GB" % (sum(sizes) / 1e9))
    print("  frames over 256 MB: %d" % sum(1 for s in sizes if s > 256 * 1024 * 1024))

    if args.verify:
        good = 0
        for archive, offset, _size in frames[:args.verify]:
            path = os.path.join(folder, "data.%03d" % archive)
            if not os.path.exists(path):
                continue
            with open(path, "rb") as handle:
                handle.seek(offset + HEADER)
                good += handle.read(4) == b"BLTE"
        print("  BLTE at +%d: %d of %d checked" % (HEADER, good, args.verify))


if __name__ == "__main__":
    main()
