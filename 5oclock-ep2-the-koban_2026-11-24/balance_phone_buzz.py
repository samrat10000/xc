from pathlib import Path
root=Path(__file__).resolve().parent
fixes={
 'audio/mix_episode.py':{'(.44,.40,.36)':'(.34,.32,.30)'},
 'audio/assemble_episode.py':{'limit=0.794:attack=3:release=80':'limit=0.710:attack=3:release=70',
                              'len(sys.argv)>2 else 2':'len(sys.argv)>2 else 3'},
 'shots/production/finish_episode.ps1':{'[int]$Version = 2':'[int]$Version = 3'},
 'shots/production/delivery_index.py':{'len(sys.argv)>1 else 2':'len(sys.argv)>1 else 3'},
}
for relative,changes in fixes.items():
    file=root/relative
    text=file.read_text(encoding='utf-8-sig')
    for old,new in changes.items():
        assert old in text, (relative,old)
        text=text.replace(old,new)
    file.write_text(text,encoding='utf-8')
