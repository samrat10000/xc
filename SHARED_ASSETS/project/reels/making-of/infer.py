import sys,os,glob,numpy as np,soundfile as sf
sys.path[:0]=[os.getcwd()+"/shim",os.getcwd(),os.getcwd()+"/GPT_SoVITS"]
from TTS_infer_pack.TTS import TTS,TTS_Config
gpt=sorted(glob.glob("GPT_weights_v2/sam-e*.ckpt"),key=os.path.getmtime)[-1]
sov=sorted(glob.glob("SoVITS_weights_v2/sam_e*.pth"),key=os.path.getmtime)[-1]
print(gpt,sov)
c=TTS_Config({"custom":{"bert_base_path":"GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large","cnhuhbert_base_path":"GPT_SoVITS/pretrained_models/chinese-hubert-base","device":"cpu","is_half":False,"t2s_weights_path":gpt,"vits_weights_path":sov,"version":"v2"}})
t=TTS(c)
ref=sys.argv[3] if len(sys.argv)>3 else "../ds/wavs/c06.wav"
pt=[l.split("|")[3].strip() for l in open("logs/sam/list.txt") if l.startswith(os.path.basename(ref))][0]
text=open(sys.argv[1]).read().strip()
out=[]
for sr,a in t.run({"text":text,"text_lang":"en","ref_audio_path":ref,"prompt_text":pt,"prompt_lang":"en","top_k":15,"top_p":1,"temperature":float(os.environ.get("GTEMP","1")),"text_split_method":"cut5","batch_size":1,"speed_factor":1.0,"repetition_penalty":1.35,"split_bucket":False,"fragment_interval":0.3,"seed":int(os.environ.get("SEED","-1"))}):
    out.append(a)
sf.write(sys.argv[2],np.concatenate(out),sr);print("saved",sys.argv[2])
