# Ep1 v2 render queue: one Blender job at a time, below-normal priority, waits while any Blender runs (Codex shares the GPU).
# Each entry: shot dir, build script, comp script, paint script, version, scale, frames. Never overwrites a version.
param([string[]]$only = @())
$ErrorActionPreference = "Stop"
$ep = Split-Path -Parent $PSScriptRoot
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"
$Q = @(
  @{ s = "16_welcome"; b = "build_s16.py"; c = "comp_s16.py"; p = "paint_bg04.py" },
  @{ s = "08_frozen";  b = "build_s08.py"; c = "comp_s08.py"; p = "paint_bg04.py" },
  @{ s = "10_eyes";    b = "build_s10.py"; c = "comp_s10.py"; p = "paint_bg04.py" }
)
foreach ($j in $Q) {
  if ($only.Count -and -not ($only -contains $j.s)) { continue }
  $src = "$ep\shots\$($j.s)\src"; $v = 2; while (Test-Path "$ep\shots\$($j.s)\v$v\full") { $v++ }
  $vd = "$ep\shots\$($j.s)\v$v"; $full = "$vd\full"; New-Item -ItemType Directory -Force $full | Out-Null
  while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 30 }
  $t0 = Get-Date; Write-Host "$($j.s) v$v start $t0"
  $p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\$($j.b)","--","$full","1.0","all" -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
  $p.PriorityClass = "BelowNormal"; $p.WaitForExit()
  $ps = if (Test-Path "$src\$($j.p)") { "$src\$($j.p)" } else { "$ep\shots\04_ride\src\$($j.p)" }
  Push-Location $full; python -I $ps "$full\meta.json" *> "$full\paint.log"; Pop-Location
  $q = Start-Process python -ArgumentList "-I","$src\$($j.c)","$full","$full\fullc" -PassThru -NoNewWindow -RedirectStandardOutput "$full\comp.log" -RedirectStandardError "$full\comp.err"
  $q.PriorityClass = "BelowNormal"; $q.WaitForExit()
  ffmpeg -y -loglevel error -framerate 24 -i "$full\fullc\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$vd\$($j.s)_v${v}_silent.mp4"
  $n = (Get-ChildItem "$full\fullc" -Filter *.png).Count
  Write-Host "$($j.s) v$v done: $n frames, $([int]((Get-Date) - $t0).TotalMinutes) min"
}
