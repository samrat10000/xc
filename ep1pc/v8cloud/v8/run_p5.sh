cd /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/ep1
lane(){ o=$1; shift; for j in "$@"; do c=${j%:*}; f=${j#*:}; CUT=$c RES=$o SAMP=12 FR=$f,$f MB=.2 OUTROOT=/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe5 timeout 1500 python3 shots2.py > /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe5/l_${c}_$f.log 2>&1 || tail -n 5 /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe5/l_${c}_$f.log; done; }
lane .5 400:62 &
lane .3 400:110 530:40 552:20 &
lane .3 535:30 540:9 565:20 &
wait
