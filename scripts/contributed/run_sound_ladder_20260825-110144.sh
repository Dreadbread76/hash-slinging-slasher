#!/bin/sh
# Scaffolding: the offset ladder (contrib/measured_offsets.py --sound) over the sound corpus,
# which no measured method had ever been given. k=12 returned 6 on Black Ops 4 where k=6 returned
# 0, so this walks deeper. Reports refusals distinctly from empty passes.
for k in 16 20 24 32 40; do
  python contrib/measured_offsets.py --sound nofold --tail $k > /dev/null 2>&1 || continue
  bin/windows/confirm_plan.exe plans/mo_snd_t$k.txt --game BLKOPS04 --no-fold --anyway > logs/snd_t${k}_BLKOPS04.log 2>&1
  if grep -q "this run added" logs/snd_t${k}_BLKOPS04.log; then
    echo "sound tails k=$k BO4 -> $(grep -oE 'this run added [0-9]+' logs/snd_t${k}_BLKOPS04.log | tail -1)"
  else
    echo "sound tails k=$k BO4 -> DID NOT RUN"
  fi
done
for k in 12 20 32; do
  python contrib/measured_offsets.py --sound fold --tail $k > /dev/null 2>&1 || continue
  bin/windows/confirm_plan.exe plans/mo_snd_t$k.txt --game BLKOPSCW --anyway > logs/snd_t${k}_BLKOPSCW.log 2>&1
  if grep -q "this run added" logs/snd_t${k}_BLKOPSCW.log; then
    echo "sound tails k=$k CW -> $(grep -oE 'this run added [0-9]+' logs/snd_t${k}_BLKOPSCW.log | tail -1)"
  else
    echo "sound tails k=$k CW -> DID NOT RUN"
  fi
done
echo "SOUND LADDER DONE"
