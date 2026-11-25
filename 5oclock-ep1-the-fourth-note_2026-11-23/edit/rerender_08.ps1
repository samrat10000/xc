# after produce_v3: re-render 08 as v4 (boy moved off the camera path)
$T = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\bndrgvou2.output"
while (-not (Select-String -Path $T -Pattern "produce_v3 done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 10 }
$ErrorActionPreference = "Continue"; $SH = (Split-Path -Parent $PSScriptRoot) + "\shots"; $src = "$SH\08_frozen\src"; $vd = "$SH\08_frozen\v4"; $full = "$vd\full"
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"; $env:SET_FWD = "1"; $env:GRIP_V3 = "1"
New-Item -ItemType Directory -Force $full | Out-Null
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 5 }
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\build_s08.py","--",$full,"1.0","all" -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
Push-Location $full; python -I "$src\paint_bg04.py" "$full\meta.json" *> "$full\paint.log"; Pop-Location
python -I "$src\comp_s08.py" $full "$full\fullc" *> "$full\comp.log"
ffmpeg -y -loglevel error -framerate 24 -i "$full\fullc\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$vd\08_frozen_v4_silent.mp4"
Write-Host "08 v4 done frames=$((Get-ChildItem "$full\fullc" -Filter *.png).Count)"
& "$SH\10b_arrive\src\run_10b.ps1" -name v2 -frames all -scale 1.0
Write-Host "10b v2 done"
