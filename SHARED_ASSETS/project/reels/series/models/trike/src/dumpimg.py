import json,struct,io,sys
from PIL import Image
b=open(sys.argv[1],'rb').read()
l=struct.unpack('<I',b[12:16])[0]; j=json.loads(b[20:20+l]); bin0=20+l+8
ims=[]
for im in j['images']:
    bv=j['bufferViews'][im['bufferView']]; d=b[bin0+bv.get('byteOffset',0):bin0+bv.get('byteOffset',0)+bv['byteLength']]
    I=Image.open(io.BytesIO(d)).convert('RGB'); I.save(f"out/tex_{im['name']}.png"); ims.append(I.resize((256,256)))
s=Image.new('RGB',(1024,512));[s.paste(x,((i%4)*256,(i//4)*256)) for i,x in enumerate(ims)];s.save('out/tex_sheet.jpg')
for m in j['materials']: print(m['name'],json.dumps(m.get('pbrMetallicRoughness'))[:200])
