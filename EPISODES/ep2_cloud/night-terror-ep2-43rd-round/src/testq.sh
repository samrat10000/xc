cd /home/user/w/sc
run(){ SHOT=$1 FRAMES=$2 FORCE=1 OUT=/home/user/w/out/shots/l$1 /home/user/bv/bin/python shots.py > /home/user/w/out/shots/logl$1.txt 2>&1; }
run 5 13,40 & run 6 13,30 & wait
run 7 20,50 & run 9 20,50 & wait
run 10 10,40 & run 4 30,50,68 & wait
echo DONE > /home/user/w/out/shots/testq.done
