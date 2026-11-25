# 006_screamer: 006a wide (0-2.5 s) rain on his window + far sirens + thunder; 006b slow-mo CU (2.5-5.5): world drops to a low rumble, slowed + pitched-down scream echoing across the street
ffmpeg -y -v error \
 -ss 5 -t 6 -i /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/sfx7/rainglass/3_c0f69197.mp3 \
 -ss 60 -t 6 -i /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/sfx7/siren/0_ead5a45b.mp3 \
 -i /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/sfx7/boom/1_2de491df.mp3 \
 -i /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/sfx7/scream/221547_4096172.mp3 \
 -i /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/sfx7/scream/333832_3840537.mp3 \
 -i /tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/sfx7/boom/1_2de491df.mp3 \
 -filter_complex "\
 [0]volume=.5,volume='if(lt(t,2.5),1,.25)':eval=frame,lowpass=f='6000'[rain];\
 [1]volume=.18,volume='if(lt(t,2.5),1,.2)':eval=frame[sir];\
 [2]volume=.9,adelay=1900|1900,lowpass=f=900[th1];\
 [5]asetrate=48000*.75,aresample=48000,volume=1.1,adelay=3450|3450,lowpass=f=600[th2];\
 [3]aresample=48000,asetrate=48000*.8,aresample=48000,volume=1.0,adelay=2550|2550,aecho=0.8:0.6:280|520:0.35|0.2,highpass=f=180[sc1];\
 [4]aresample=48000,asetrate=48000*.8,aresample=48000,volume=.45,adelay=2920|2920,aecho=0.8:0.6:300:0.3,highpass=f=120[sc2];\
 [rain][sir][th1][th2][sc1][sc2]amix=inputs=6:normalize=0,afade=t=out:st=5.2:d=0.3,alimiter=limit=.89,loudnorm=I=-17:TP=-1.5[o]" \
 -map "[o]" -t 5.5 -ar 48000 -ac 2 006_snd.wav
