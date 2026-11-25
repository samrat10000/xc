# shot 15 v4 (scarier Listener, no shards): build -> comp -> (encode when all).  usage: run_v4.ps1 -name v4_probe -frames "40,70,85,100" -scale 0.5
param([string]$name = "v4", [string]$frames = "all", [string]$scale = "1.0")
$src = $PSScriptRoot; $full = (Resolve-Path "$src\..").Path + "\$name\full"
New-Item -ItemType Directory -Force $full, "$full\fullc" | Out-Null
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 3 }
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\build_s15_v4.py","--","$full",$scale,$frames -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
Push-Location $src
if ($frames -eq "all") { python -E -s comp_s15_v4.py "$full" "$full\fullc" *> "$full\comp.log" } else { python -E -s comp_s15_v4.py "$full" "$full\fullc" $frames *> "$full\comp.log" }
Pop-Location
if ($frames -eq "all") { ffmpeg -y -loglevel error -framerate 24 -i "$full\fullc\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p ((Resolve-Path "$src\..").Path + "\$name\15_listener_${name}_silent.mp4") }
$e = Select-String -Path "$full\build.err","$full\comp.log" -Pattern "Error|Traceback" | Select-Object -First 4
Write-Host "15 $name done errors=$($e.Count)"; $e | % { Write-Host $_.Line }
