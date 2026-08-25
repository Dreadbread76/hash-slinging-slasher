#!/bin/sh
while tasklist //FI "IMAGENAME eq confirm_plan.exe" 2>/dev/null | grep -q confirm_plan; do sleep 30; done
bin/windows/confirm_plan.exe plans/shell_h6t6.txt > logs/shell_h6t6_BLKOPSCW.log 2>&1
echo "SHELLS CW DONE"
bin/windows/confirm_plan.exe plans/shell_h6t6.txt --game BLKOPS04 > logs/shell_h6t6_BLKOPS04.log 2>&1
echo "SHELLS BO4 DONE"
