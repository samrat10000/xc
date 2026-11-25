#!/bin/bash
# master.sh in.wav out.wav : -14 LUFS integrated, -1.5 dBTP (iterate gain into a limiter)
in=$1; out=$2; g=0
for it in 1 2 3 4; do
  ffmpeg -y -v error -i $in -af "volume=${g}dB,alimiter=limit=0.74:attack=1:release=60:level=false" -ar 48000 /tmp/_m.wav
  I=$(ffmpeg -v info -i /tmp/_m.wav -af ebur128=peak=true -f null - 2>&1 | grep -A3 "Integrated" | grep "I:" | awk '{print $2}')
  echo "it $it gain $g I $I"
  g=$(python3 -c "print(round($g + (-14.0 - $I) * 1.1, 2))")
  python3 -c "import sys; sys.exit(0 if abs($I + 14) < .4 else 1)" && break
done
cp /tmp/_m.wav $out
