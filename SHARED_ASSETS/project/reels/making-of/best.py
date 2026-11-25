import sys,torch,torchaudio as ta,difflib,re
from chatterbox.tts import ChatterboxTTS
from faster_whisper import WhisperModel
torch.set_num_threads(4)
m=ChatterboxTTS.from_pretrained(device="cpu");asr=WhisperModel("small",device="cpu",compute_type="int8")
norm=lambda s:re.sub(r"[^a-z ]","",s.lower().replace("three twelve a.m.","312 am"))
lines=open(sys.argv[1]).read().strip().split("\n");outs=[]
for i,l in enumerate(lines):
    best=None
    for k in range(3):
        w=m.generate(l,audio_prompt_path="ref.wav",exaggeration=0.6,cfg_weight=0.4,temperature=0.8)
        ta.save("tmp.wav",w,m.sr)
        t=" ".join(s.text for s in asr.transcribe("tmp.wav",language="en")[0])
        sc=difflib.SequenceMatcher(None,norm(l),norm(t.replace("3.12","312").replace("3:12","312"))).ratio()
        print(i,k,round(sc,3),t,flush=True)
        if best is None or sc>best[0]: best=(sc,w)
        if sc>0.97: break
    outs+= [best[1],torch.zeros(1,int(m.sr*0.2))]
ta.save(sys.argv[2],torch.cat(outs,1),m.sr)
print("DONE")
