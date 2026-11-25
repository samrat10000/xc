cd /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/ep1
lane(){ o=$1; shift; for j in "$@"; do c=${j%:*}; f=${j#*:}; CUT=$c RES=$o SAMP=12 FR=$f,$f MB=.2 OUTROOT=/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3 timeout 1500 python3 shots2.py > /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3/l_${c}_$f.log 2>&1 || tail -n 5 /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3/l_${c}_$f.log; done; }
(rm -f /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3/c400/f0062.png; lane .3 400:110; CUT=400 RES=.6 SAMP=16 FR=62,62 MB=.2 OUTROOT=/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe4 python3 shots2.py > /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/v8/probe3/l_hi62.log 2>&1) &
lane .3 530:40 535:30 540:9 550:52 552:20 565:20 &
wait
