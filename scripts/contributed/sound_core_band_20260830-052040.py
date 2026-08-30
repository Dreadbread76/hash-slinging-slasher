"""Stage a bounded, reproducible band of the confirmed sound cores."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "contrib" / "ab_sound_cores.txt"
target = ROOT / "contrib" / "ab_sound_cores_band_20260830.txt"

cores = [line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
# The source is sorted by the producer.  A bounded prefix is a distinct, auditable
# candidate band and keeps each checkpoint small enough to complete.
band = cores[:2000]
target.write_text("\n".join(band) + "\n", encoding="utf-8")
print(f"staged {len(band)} of {len(cores)} confirmed sound cores")
