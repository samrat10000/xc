"""Assemble actual rendered shot frames into a labeled review sheet, no fake frames."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--version',default='v004');a=p.parse_args();plan=json.loads((ROOT/'SHOTS.json').read_text())
W,H=216,384;PAD=16;LABEL=52;COLS=5;ROWS=4
sheet=Image.new('RGB',(PAD+COLS*(W+PAD),84+ROWS*(H+LABEL+PAD)),(12,16,21));d=ImageDraw.Draw(sheet)
try:font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15);title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
except OSError:font=title=ImageFont.load_default()
d.text((PAD,12),'TUNNEL VISION / EPISODE 3',fill='white',font=title);d.text((PAD,46),f'{a.version} - BLOCKING / framing review, unfinished motion and audio',fill=(226,182,108),font=font)
for shot in plan['shots']:
 n=shot['n'];x=PAD+(n-1)%COLS*(W+PAD);y=84+(n-1)//COLS*(H+LABEL+PAD);files=sorted((ROOT/'frames'/a.version/f'shot{n:02d}').glob('f*.png'))
 if files:
  frame=files[len(files)//2];im=Image.open(frame).convert('RGB');im.thumbnail((W,H));sheet.paste(im,(x+(W-im.width)//2,y+(H-im.height)//2))
 else:d.rectangle((x,y,x+W,y+H),outline=(68,76,85));d.text((x+10,y+H//2),'PENDING',fill=(150,157,165),font=font)
 d.text((x,y+H+6),f'{n:02d}  {shot["name"]}',fill='white',font=font);d.text((x,y+H+27),shot['time_s']+' s',fill=(153,169,185),font=font)
dest=ROOT/'out'/f'ep3-{a.version}-contact-sheet.jpg';sheet.save(dest,quality=94);print(dest)
