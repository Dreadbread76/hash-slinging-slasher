#!/bin/sh
# Scaffolding, not a method and NOT a rotation: this walks the rungs of ONE invented
# method (contrib/measured_offsets.py, METHODS 33/34) across two games, because each rung
# is twenty seconds and the yield rises with k. CLAUDE.md forbids a driver that runs every
# existing method in order; this runs one method at every depth. Delete it once the ladder
# is ground out -- it has no value of its own.
for k in 4 5 6 10 12 14 16 20 24; do
  python contrib/measured_offsets.py --tail $k > /dev/null 2>&1 || continue
  for g in BLKOPSCW BLKOPS04; do
    bin/windows/confirm_plan.exe plans/mo_t$k.txt --game $g > logs/mo_t${k}_${g}.log 2>&1
    echo "tails k=$k $g -> $(grep -oE 'this run added [0-9]+' logs/mo_t${k}_${g}.log | tail -1)"
  done
done
for k in 4 6 8 10 16 20 24; do
  python contrib/measured_offsets.py --head $k > /dev/null 2>&1 || continue
  for g in BLKOPSCW BLKOPS04; do
    bin/windows/confirm_plan.exe plans/mo_h$k.txt --game $g > logs/mo_h${k}_${g}.log 2>&1
    echo "heads k=$k $g -> $(grep -oE 'this run added [0-9]+' logs/mo_h${k}_${g}.log | tail -1)"
  done
done
echo "WIDE LADDER DONE"
