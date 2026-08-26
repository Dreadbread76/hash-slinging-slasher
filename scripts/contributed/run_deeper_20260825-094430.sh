#!/bin/sh
# Scaffolding, not a method: the ladder of contrib/measured_offsets.py has not flattened at k=48,
# so this walks further out in both directions. Reports refusals distinctly from empty passes.
for d in h t; do
  for k in 28 32 40 56 64; do
    [ "$d" = h ] && flag="--head" || flag="--tail"
    [ "$d" = h ] && [ $k -lt 56 ] && continue
    python contrib/measured_offsets.py $flag $k > /dev/null 2>&1 || continue
    for g in BLKOPS04 BLKOPSCW; do
      bin/windows/confirm_plan.exe plans/mo_$d$k.txt --game $g > logs/mo_${d}${k}_${g}.log 2>&1
      if grep -q "this run added" logs/mo_${d}${k}_${g}.log; then
        echo "$d k=$k $g -> $(grep -oE 'this run added [0-9]+' logs/mo_${d}${k}_${g}.log | tail -1)"
      else
        echo "$d k=$k $g -> DID NOT RUN (guard or error)"
      fi
    done
  done
done
echo "DEEPER DONE"
