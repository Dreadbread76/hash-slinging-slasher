"""Probe the uncarried BO4 sound-alias family ``bik_execution_``.

The family is prominent in the seam audit but its leading cut is absent from
data/prefixes.txt, so normal recombination never emits it.  Existing names
show a compact numeric suffix; enumerate the fixed-width numeric namespace
directly and let confirm_list prove any hits.
"""
from pathlib import Path

for width in (3, 4):
    for i in range(10 ** width):
        yield_name = f"bik_execution_{i:0{width}d}"
        print(yield_name)

