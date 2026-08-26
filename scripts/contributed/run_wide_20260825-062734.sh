#!/bin/sh
# Scaffolding, not a method and NOT a rotation: this walks the rungs of ONE invented
# method (contrib/measured_offsets.py, METHODS 33/34) across two games, because each rung
# is twenty seconds and the yield rises with k. CLAUDE.md forbids a driver that runs every
# existing method in order; this runs one method at every depth. Delete it once the ladder
# is ground out -- it has no value of its own.
while tasklist //FI "IMAGENAME eq confirm_plan.exe" 2>/dev/null | grep -q confirm_plan; do sleep 30; done
for spec in "mo_t8" "mo_h12"; do
  for g in BLKOPSCW BLKOPS04; do
    echo "===== $spec $g"
    bin/windows/confirm_plan.exe plans/$spec.txt --game $g > logs/${spec}_${g}.log 2>&1
  done
done
echo "WIDE DONE"
