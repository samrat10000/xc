from pathlib import Path
p=Path(__file__).resolve().parent
f=p/'station_v6.py'
s=f.read_text(encoding='utf-8-sig')
a,b=s.index('def shot_07()'),s.index('def shot_10()')
s=s[:a]+s[a:b].replace('interval(f,1,120)','interval(f,1,128)').replace('return 120,frame','return 128,frame')+s[b:]
a=s.index('def shot_15()')
s=s[:a]+s[a:].replace('interval(f,1,72)','interval(f,1,96)').replace('return 72,frame','return 96,frame')
compile(s,str(f),'exec')
f.write_text(s,encoding='utf-8')
f=p/'run_shot.ps1'
s=f.read_text(encoding='utf-8-sig')
old='if(!$card){throw "Unknown shot $Shot"}'
new=old+"""
if($env:KOBAN_PICTURE_REVISION -eq '6'){
    if($Shot -eq '07'){$card.frames=128; $card.keys=@(1,18,35,61,87,128); $card.stills=@(1,19,68,128)}
    if($Shot -eq '15'){$card.frames=96; $card.keys=@(1,18,34,52,75,96); $card.stills=@(1,32,60,96)}
}"""
assert old in s
f.write_text(s.replace(old,new),encoding='utf-8')
