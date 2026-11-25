$ErrorActionPreference = "Stop"
$src = $PSScriptRoot; $v = (Resolve-Path "$src\..").Path + "\v1"; $full = "$v\full"
if (Test-Path $full) { throw "v1\full exists" }
New-Item -ItemType Directory -Force $full | Out-Null; $t0 = Get-Date
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\build_s14.py","--","$full","1.0","all" -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit(); "build " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$v\timing.txt"
$m = Get-Content "$full\meta.json" -Raw | ConvertFrom-Json
Push-Location $src
python paint_bg.py "$full\bg.png" $m.'37'.sx $m.'37'.sy *> "$full\paint.log"
python ecu_s14.py "$full" "$full\fullc" *> "$full\ecu.log"
python comp_s14.py "$full" "$full\bg.png" "$full\fullc" *> "$full\comp.log"
Pop-Location
"comp " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$v\timing.txt" -Append
ffmpeg -y -loglevel error -framerate 24 -i "$full\fullc\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$v\14_fourth_v1_silent.mp4"
"encode " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$v\timing.txt" -Append