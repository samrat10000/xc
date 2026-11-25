cd /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/ep1
lane(){ for j in "$@"; do c=${j%:*}; f=${j#*:}; CUT=$c RES=.3 SAMP=12 FR=$f,$f MB=.2 OUTROOT=/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3 timeout 1500 python3 shots2.py > /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3/l_${c}_$f.log 2>&1 || tail -n 5 /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3/l_${c}_$f.log; done; }
lane 400:62 400:84 400:110 525:80 525:106 525:124 &
lane 530:40 535:30 540:9 550:52 552:20 565:20 495:30 &
wait
