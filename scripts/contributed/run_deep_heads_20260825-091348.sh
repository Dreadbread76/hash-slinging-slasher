#!/bin/sh
# Scaffolding, not a method: deeper rungs of contrib/measured_offsets.py --head, because k=16
# and k=24 were still returning 136 and 91 on Black Ops 4. Delete once the ladder flattens.
for k in 28 32 40 48; do
  python contrib/measured_offsets.py --head $k > /dev/null 2>&1 || continue
  for g in BLKOPS04 BLKOPSCW; do
    bin/windows/confirm_plan.exe plans/mo_h$k.txt --game $g > logs/mo_h${k}_${g}.log 2>&1
    if grep -q "this run added" logs/mo_h${k}_${g}.log; then
      echo "heads k=$k $g -> $(grep -oE 'this run added [0-9]+' logs/mo_h${k}_${g}.log | tail -1)"
    else
      echo "heads k=$k $g -> DID NOT RUN (guard or error)"
    fi
  done
done
echo "DEEP HEADS DONE"
