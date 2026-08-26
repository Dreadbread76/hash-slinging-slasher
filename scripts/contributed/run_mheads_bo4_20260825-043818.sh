#!/bin/sh
while tasklist //FI "IMAGENAME eq confirm_plan.exe" 2>/dev/null | grep -q confirm_plan; do sleep 20; done
for k in 4 5 6 8 10 12 14 16 20; do
  echo "===== mheads k=$k BLKOPS04"
  bin/windows/confirm_plan.exe plans/mheads$k.txt --game BLKOPS04 > logs/mheads${k}_BLKOPS04.log 2>&1
done
echo "BO4 LADDER DONE"
