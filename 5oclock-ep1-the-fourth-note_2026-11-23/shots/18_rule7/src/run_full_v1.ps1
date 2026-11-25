$src = $PSScriptRoot; $v = (Resolve-Path "$src\..").Path + "\v1"; $full = "$v\fullc"
if (Test-Path $full) { throw "exists" }
$t0 = Get-Date
$q = Start-Process python -ArgumentList "-I","$src\make_s18.py","$full" -PassThru -NoNewWindow -RedirectStandardOutput "$v\make.log" -RedirectStandardError "$v\make.err"
$q.PriorityClass = "BelowNormal"; $q.WaitForExit()
ffmpeg -y -loglevel error -framerate 24 -i "$full\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$v\18_rule7_v1_silent.mp4"
"done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$v\timing.txt"