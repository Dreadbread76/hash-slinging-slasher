#!/bin/sh
# Scaffolding, not a method and NOT a rotation: this walks the rungs of ONE invented
# method (contrib/measured_offsets.py, METHODS 33/34) across two games, because each rung
# is twenty seconds and the yield rises with k. CLAUDE.md forbids a driver that runs every
# existing method in order; this runs one method at every depth. Delete it once the ladder
# is ground out -- it has no value of its own.
while tasklist //FI "IMAGENAME eq confirm_plan.exe" 2>/dev/null | grep -q confirm_plan; do sleep 30; done
bin/windows/confirm_plan.exe plans/shell_h6t6.txt > logs/shell_h6t6_BLKOPSCW.log 2>&1
echo "SHELLS CW DONE"
bin/windows/confirm_plan.exe plans/shell_h6t6.txt --game BLKOPS04 > logs/shell_h6t6_BLKOPS04.log 2>&1
echo "SHELLS BO4 DONE"
