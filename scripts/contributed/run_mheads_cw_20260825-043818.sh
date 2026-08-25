#!/bin/sh
for k in 4 5 6 8 10 12 14 16 20; do
  echo "===== mheads k=$k BLKOPSCW"
  bin/windows/confirm_plan.exe plans/mheads$k.txt > logs/mheads${k}_BLKOPSCW.log 2>&1
  tail -3 logs/mheads${k}_BLKOPSCW.log | grep -E "total:|added" 
done
echo "LADDER DONE"
