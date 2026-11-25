from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'run_shot.ps1'
s=p.read_text(encoding='utf-8-sig')
s=s.replace('    [string]$Frames,','    [string]$Frames,\n    [switch]$Resume,')
old="$keys=if($Mode -eq 'Master'){'all'}elseif($Frames){$Frames}else{$card.keys -join ','}"
new="""if($Resume -and $Mode -ne 'Master'){throw 'Resume applies only to an interrupted master.'}
if($Resume){
    python (Join-Path $PSScriptRoot 'verify_partial.py') $cel
    if($LASTEXITCODE -ne 0){throw 'Could not verify the interrupted cels.'}
}
$keys=if($Resume){'resume'}elseif($Mode -eq 'Master'){'all'}elseif($Frames){$Frames}else{$card.keys -join ','}"""
assert old in s
p.write_text(s.replace(old,new),encoding='utf-8')
p=root/'build_reel.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("frames=range(1,duration+1) if args[3]=='all'", "frames=range(1,duration+1) if args[3] in ('all','resume')")
s=s.replace("if args[3]!='all' or f in preflight_frames:","if args[3] not in ('all','resume') or f in preflight_frames:")
old="    render(OUT/f'cel_{f:03d}.png')"
assert old in s
s=s.replace(old,"""    path=OUT/f'cel_{f:03d}.png'
    if args[3]!='resume' or not path.exists():
        render(path)""")
p.write_text(s,encoding='utf-8')
