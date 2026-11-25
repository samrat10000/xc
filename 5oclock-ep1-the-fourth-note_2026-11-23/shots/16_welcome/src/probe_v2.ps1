# v2 probe: waits until Blender is free (Codex shares the GPU), renders the given frames at 50% and comps them.
# usage: probe_v2.ps1 <outname> <frames>   e.g. probe_v2.ps1 v2_probeB "1,30,60"
param([string]$name = "v2_probe", [string]$frames = "18,19,20,21,22,23,24")
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot; $out = (Resolve-Path "$src\..").Path + "\$name"
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 20 }
New-Item -ItemType Directory -Force $out | Out-Null
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\build_s16.py","--","$out","0.5",$frames -PassThru -NoNewWindow -RedirectStandardOutput "$out\build.log" -RedirectStandardError "$out\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
Push-Location $out; python -I "$src\paint_bg04.py" "$out\meta.json" *> "$out\paint.log"; Pop-Location
python -I "$src\comp_s16.py" $out "$out\fullc" *> "$out\comp.log"
Write-Host "probe done $name"
