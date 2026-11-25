import sys,torch,torchaudio as ta,time
from chatterbox.tts import ChatterboxTTS
torch.set_num_threads(4)
m=ChatterboxTTS.from_pretrained(device="cpu")
lines=open(sys.argv[1]).read().strip().split("\n")
outs=[]
for i,l in enumerate(lines):
    t=time.time()
    w=m.generate(l,audio_prompt_path="ref.wav",exaggeration=float(sys.argv[3]),cfg_weight=float(sys.argv[4]),temperature=0.8)
    outs.append(w); outs.append(torch.zeros(1,int(m.sr*0.18)))
    print(i,round(time.time()-t,1),"s",flush=True)
ta.save(sys.argv[2],torch.cat(outs,1),m.sr)
