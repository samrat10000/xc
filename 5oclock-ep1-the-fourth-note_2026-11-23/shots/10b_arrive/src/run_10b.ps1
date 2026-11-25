# shot 10b: build (GPU, waits for a free Blender) -> paint bg -> comp (black glass) -> encode.  usage: run_10b.ps1 -name v3_probe -frames "1,16,30,48" -scale 0.5
param([string]$name = "v1", [string]$frames = "all", [string]$scale = "1.0")
$src = $PSScriptRoot; $v = (Resolve-Path "$src\..").Path + "\$name"; $full = "$v\full"
New-Item -ItemType Directory -Force $full | Out-Null
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 3 }
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\build_s10b.py","--","$full",$scale,$frames -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
$m = Get-Content "$full\meta.json" -Raw | ConvertFrom-Json; $f1 = ($m.PSObject.Properties | Select-Object -First 1).Value
Push-Location $src
python -E -s paint_bg.py "$full\bg.png" $f1.sx $f1.sy *> "$full\paint.log"
python -E -s comp_s10b.py "$full" "$full\bg.png" "$full\fullc" *> "$full\comp.log"
Pop-Location
if ($frames -eq "all") { ffmpeg -y -loglevel error -framerate 24 -i "$full\fullc\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$v\10b_arrive_${name}_silent.mp4" }
$e = Select-String -Path "$full\build.err","$full\comp.log" -Pattern "Error|Traceback" | Select-Object -First 4
Write-Host "10b $name done errors=$($e.Count)"; $e | % { Write-Host $_.Line }
