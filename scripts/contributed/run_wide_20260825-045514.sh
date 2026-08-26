#!/bin/sh
while tasklist //FI "IMAGENAME eq confirm_plan.exe" 2>/dev/null | grep -q confirm_plan; do sleep 30; done
for spec in "mo_t8" "mo_h12"; do
  for g in BLKOPSCW BLKOPS04; do
    echo "===== $spec $g"
    bin/windows/confirm_plan.exe plans/$spec.txt --game $g > logs/${spec}_${g}.log 2>&1
  done
done
echo "WIDE DONE"
