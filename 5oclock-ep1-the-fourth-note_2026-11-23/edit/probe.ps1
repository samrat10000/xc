# Generic probe: waits for a free Blender (shared GPU), renders <frames> of a shot at 50% into shots/<shot>/<name>, comps them.
# usage: probe.ps1 -shot 09_silence -frames "18,24,30" [-name v2_probe] [-build build_s09.py] [-comp comp_s09.py]
param([string]$shot, [string]$frames, [string]$name = "v2_probe", [string]$build = "", [string]$comp = "", [string]$extra = "")
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $src = "$ep\shots\$shot\src"; $n = $shot.Substring(0, 2)
if (-not $build) { $build = "build_s$n.py" }; if (-not $comp) { $comp = "comp_s$n.py" }
$out = "$ep\shots\$shot\$name"; if (Test-Path $out) { Remove-Item "$out\*" -Recurse -Force }; New-Item -ItemType Directory -Force $out | Out-Null   # fresh dir: stale cels crashed a comp
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"; $env:SET_FWD = "1"; $env:GRIP_V3 = "1"
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 3 }
$al = @("-b","--python","$src\$build","--","$out","0.5",$frames); if ($extra) { $al += $extra }
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList $al -PassThru -NoNewWindow -RedirectStandardOutput "$out\build.log" -RedirectStandardError "$out\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
$ps = if (Test-Path "$src\paint_bg04.py") { "$src\paint_bg04.py" } else { "$ep\shots\04_ride\src\paint_bg04.py" }
if (Test-Path "$src\$comp") {
  if (Select-String -Path "$src\$comp" -Pattern "bg04|paint_bg|sky04" -Quiet) { Push-Location $out; python -I $ps "$out\meta.json" *> "$out\paint.log"; Pop-Location }
  python -I "$src\$comp" $out "$out\fullc" *> "$out\comp.log"
}
$e = Select-String -Path "$out\build.err" -Pattern "Error|Traceback" | Select-Object -First 3
Write-Host "probe done $shot $name frames=$frames errors=$($e.Count)"; $e | % { Write-Host $_.Line }




