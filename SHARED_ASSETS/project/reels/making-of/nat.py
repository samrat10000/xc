import sys,torch,torchaudio as ta
from chatterbox.tts import ChatterboxTTS
torch.set_num_threads(4)
m=ChatterboxTTS.from_pretrained(device="cpu")
ref,out,ex,cfg,temp=sys.argv[2],sys.argv[3],float(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6])
outs=[]
for l in open(sys.argv[1]).read().strip().split("\n"):
    outs+=[m.generate(l,audio_prompt_path=ref,exaggeration=ex,cfg_weight=cfg,temperature=temp),torch.zeros(1,int(m.sr*0.35))]
    print("line",flush=True)
ta.save(out,torch.cat(outs,1),m.sr)
