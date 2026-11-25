S=/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad; cd $S/pent7
COMMON="SAMBLEND=$S/cast/sam/sam.blend CASTLIB=$S/cast PLATE=$PWD/nyc_plate_clean.png TSIDE=-1 ANIM=1 RENDER_ANIM=1 FIREL=.35 LAMP=.25 CITYGLOW=.3 CITYCOL=#8a9cc8 FIRE_E=2.5 TONGUE=.3 NOSMOKE=1 RES=1080 SPP=32"
env $COMMON PHONE_PNG=$PWD/phone_screen_connected.png CAMV=g KITCHEN=1 NFRAMES=48 BUZZ=-100 LIFT0=1 LIFT1=2 W0=1 EAR0=0 EAR1=1 ERUPT_F=-60 GLOW=2 OUT=$PWD/out007v8/f python3 pent7.py > out007v8.log 2>&1; echo 007 done
