# shot 09 full render (below-normal priority). Refuses to overwrite.
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot; $v = (Resolve-Path "$src\..").Path + "\v1"; $full = "$v\full"
if (Test-Path $full) { throw "v1\full exists: bump the version" }
New-Item -ItemType Directory -Force $full | Out-Null
$t0 = Get-Date
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\build_s09.py","--","$full","1.0","all" -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
"build done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$full\timing.txt"
Push-Location $full; python -I "$src\paint_bg04.py" "$full\meta.json" *> "$full\paint.log"; Pop-Location
$q = Start-Process python -ArgumentList "-I","$src\comp_s09.py","$full","$full\fullc" -PassThru -NoNewWindow -RedirectStandardOutput "$full\comp.log" -RedirectStandardError "$full\comp.err"
$q.PriorityClass = "BelowNormal"; $q.WaitForExit()
"comp done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$full\timing.txt" -Append
ffmpeg -y -loglevel error -framerate 24 -i "$full\fullc\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$v\09_silence_v1_silent.mp4"
"encode done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$full\timing.txt" -Append