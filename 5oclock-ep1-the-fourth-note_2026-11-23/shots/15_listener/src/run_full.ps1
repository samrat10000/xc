# full render of shot 15 test v1 on this PC at below-normal priority. Refuses to overwrite an existing v1\full.
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot; $v = (Resolve-Path "$src\..").Path + "\v1"
$full = "$v\full"; if (Test-Path $full) { throw "v1\full exists: bump the version" }
New-Item -ItemType Directory -Force $full, "$full\fullc" | Out-Null
$blender = "c:\Users\cross\Downloads\xc\blender501\blender.exe"
$t0 = Get-Date
$p = Start-Process $blender -ArgumentList "-b","--python","$src\build_s15.py","--","$full","1.0","all" -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
"build done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$full\timing.txt"
$q = Start-Process python -ArgumentList "-I","$src\comp_s15.py","$full","$full\fullc" -PassThru -NoNewWindow -RedirectStandardOutput "$full\comp.log" -RedirectStandardError "$full\comp.err"
$q.PriorityClass = "BelowNormal"; $q.WaitForExit()
"comp done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$full\timing.txt" -Append
ffmpeg -y -framerate 24 -i "$full\fullc\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$v\15_listener_v1_silent.mp4" 2> "$full\ffmpeg.log"
"encode done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$full\timing.txt" -Append