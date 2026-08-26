#!/bin/sh
# Scaffolding, not a method and NOT a rotation: the heads rungs of contrib/measured_offsets.py
# that the futility guard refused while a repeated tails round was running. Delete after use.
for k in 10 4 6 8 16 20 24; do
  for g in BLKOPS04 BLKOPSCW; do
    [ -f plans/mo_h$k.txt ] || continue
    bin/windows/confirm_plan.exe plans/mo_h$k.txt --game $g > logs/mo_h${k}_${g}.log 2>&1
    echo "heads k=$k $g -> $(grep -oE 'this run added [0-9]+' logs/mo_h${k}_${g}.log | tail -1)"
  done
done
echo "HEADS HALF DONE"
