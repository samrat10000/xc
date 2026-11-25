from pathlib import Path

root=Path(__file__).resolve().parent
p=root/'stage.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("PROJECT=ROOT.parents[1]\nCANON=PROJECT.parent/'5oclock-ep1-the-fourth-note_2026-11-23'","PROJECT=ROOT.parent")
s=s.replace("PROJECT/'toon3d'/'sam_toon_003.blend'","ASSETS/'sam_toon.blend'").replace("CANON/'assets'/'cast'","ASSETS/'cast'")
s=s.replace("PROJECT/'ep2_codex'/'02_wrong_room'","PROJECT/'02_wrong_room'")
p.write_text(s,encoding='utf-8')
p=root/'run_shot.ps1'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("{'0.43'}","{'0.50'}")
line='& $Blender -b -t 6 --factory-startup --python-exit-code 1 -P (Join-Path $PSScriptRoot \'build_reel.py\') -- $Shot $cel $scale $keys *> $log\nif($LASTEXITCODE -ne 0){Get-Content -Tail 30 -LiteralPath $log;throw "Blender failed in shot $Shot"}'
launch='''$blenderScript=Join-Path $PSScriptRoot 'build_reel.py'
$launchArgs=@('-b','-t','6','--factory-startup','--python-exit-code','1','-P',"`"$blenderScript`"",'--',$Shot,"`"$cel`"",$scale,$keys)
$render=Start-Process -FilePath $Blender -ArgumentList $launchArgs -RedirectStandardOutput $log -RedirectStandardError "$log.stderr" -WindowStyle Hidden -PassThru
try {$render.PriorityClass='BelowNormal'} catch {Write-Verbose 'Blender exited before priority could be set.'}
$render.WaitForExit()
if($render.ExitCode -ne 0){Get-Content -Tail 25 -LiteralPath $log,"$log.stderr";throw "Blender failed in shot $Shot"}'''
assert line in s
p.write_text(s.replace(line,launch),encoding='utf-8')
