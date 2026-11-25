import sys,os,glob,re,difflib,numpy as np,soundfile as sf
sys.path[:0]=[os.getcwd()+"/shim",os.getcwd(),os.getcwd()+"/GPT_SoVITS"]
from TTS_infer_pack.TTS import TTS,TTS_Config
from faster_whisper import WhisperModel
gpt=sys.argv[3]; sov=sorted(glob.glob("SoVITS_weights_v2/sam_e*.pth"),key=os.path.getmtime)[-1]
t=TTS(TTS_Config({"custom":{"bert_base_path":"GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large","cnhuhbert_base_path":"GPT_SoVITS/pretrained_models/chinese-hubert-base","device":"cpu","is_half":False,"t2s_weights_path":gpt,"vits_weights_path":sov,"version":"v2"}}))
asr=WhisperModel("small",device="cpu",compute_type="int8")
ref="../ds/wavs/c06.wav"; pt=[l.split("|")[3].strip() for l in open("logs/sam/list.txt") if l.startswith("c06")][0]
norm=lambda s:re.sub(r"[^a-z ]","",s.lower())
out=[];sr0=32000
for i,l in enumerate(open(sys.argv[1]).read().strip().split("\n")):
    best=None
    for k in range(5):
        a=[x for _,x in [(s,x) for s,x in t.run({"text":l,"text_lang":"en","ref_audio_path":ref,"prompt_text":pt,"prompt_lang":"en","top_k":5,"top_p":1,"temperature":0.6,"text_split_method":"cut0","batch_size":1,"speed_factor":1.0,"repetition_penalty":1.35,"split_bucket":False,"fragment_interval":0.3,"seed":1000+k})]]
        w=np.concatenate(a); sf.write("tmp.wav",w,sr0)
        tx=" ".join(s.text for s in asr.transcribe("tmp.wav",language="en")[0])
        sc=difflib.SequenceMatcher(None,norm(l.replace("three twelve A.M.","312 am")),norm(tx.replace("3.12","312").replace("3:12","312"))).ratio()
        print(i,k,round(sc,3),tx,flush=True)
        if best is None or sc>best[0]: best=(sc,w)
        if sc>0.93: break
    out+=[best[1],np.zeros(int(sr0*0.3))]
sf.write(sys.argv[2],np.concatenate(out),sr0);print("DONE")
