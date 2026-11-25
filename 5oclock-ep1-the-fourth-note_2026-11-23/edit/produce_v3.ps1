# Ep1 v3 full renders (Sam's v2 notes). One waiter, one Blender at a time, below-normal. Waits for the probe chains first.
# Order: approved first (04, 09, 05, 08), then the ones whose re-probes are checked while these render (10b, 15, 17).
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $SH = "$ep\shots"; $B = "c:\Users\cross\Downloads\xc\blender501\blender.exe"
$T = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks"
while (-not (Select-String -Path "$T\bg4p9nnd6.output" -Pattern "chain v3g done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 10 }
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"; $env:SET_FWD = "1"; $env:GRIP_V3 = "1"; $env:NIGHT_SPRITES = "$SH\11_mirror\crowd_sprites"
function Wait-Free { while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 5 } }
function Run-Blender($argl, $log) { Wait-Free; $p = Start-Process $B -ArgumentList $argl -PassThru -NoNewWindow -RedirectStandardOutput "$log.log" -RedirectStandardError "$log.err"; $p.PriorityClass = "BelowNormal"; $p.WaitForExit() }
function Encode($dir, $mp4) { ffmpeg -y -loglevel error -framerate 24 -i "$dir\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $mp4; Write-Host "$(Get-Date -Format HH:mm) encoded $(Split-Path $mp4 -Leaf) frames=$((Get-ChildItem $dir -Filter *.png).Count)" }
function Shot($s, $ver) {
  $n = $s.Substring(0, 2); $src = "$SH\$s\src"; $vd = "$SH\$s\$ver"; $full = "$vd\full"; New-Item -ItemType Directory -Force $full | Out-Null
  Run-Blender @("-b", "--python", "$src\build_s$n.py", "--", $full, "1.0", "all") "$full\build"
  $ps = if (Test-Path "$src\paint_bg04.py") { "$src\paint_bg04.py" } else { "$SH\04_ride\src\paint_bg04.py" }
  Push-Location $full; python -I $ps "$full\meta.json" *> "$full\paint.log"; Pop-Location
  python -I "$src\comp_s$n.py" $full "$full\fullc" *> "$full\comp.log"
  Encode "$full\fullc" "$vd\${s}_${ver}_silent.mp4"
}
Shot '04_ride' 'v5'
Shot '09_silence' 'v3'
# 05 v4: cuts a + c re-rendered, cut b (kids, unchanged) reused from v3
$v = "$SH\05_ritual\v4"; $all = "$v\fullc"; New-Item -ItemType Directory -Force $all | Out-Null; $k = 0
foreach ($cut in 'a', 'b', 'c') {
  if ($cut -eq 'b') { $cdir = "$SH\05_ritual\v3\full_b\c" } else {
    $full = "$v\full_$cut"; New-Item -ItemType Directory -Force $full | Out-Null
    Run-Blender @("-b", "--python", "$SH\05_ritual\src\build_s05.py", "--", $full, "1.0", "all", $cut) "$full\build"
    Push-Location $full; python -I "$SH\05_ritual\src\paint_bg04.py" "$full\meta.json" *> "$full\paint.log"; Pop-Location
    python -I "$SH\05_ritual\src\comp_s05.py" $full "$full\c" *> "$full\comp.log"; $cdir = "$full\c" }
  foreach ($f in 1..28) { $k++; Copy-Item ("$cdir\{0:D3}.png" -f $f) ("$all\{0:D3}.png" -f $k) }
}
Encode $all "$v\05_ritual_v4_silent.mp4"
Shot '08_frozen' 'v3'
& "$SH\10b_arrive\src\run_10b.ps1" -name v1 -frames all -scale 1.0
& "$SH\15_listener\src\run_v4.ps1" -name v4 -frames all -scale 1.0
$day = "$SH\17_wrongside\v3\day"; New-Item -ItemType Directory -Force $day | Out-Null
Run-Blender @("-b", "--python", "$SH\17_wrongside\src\build_s17_day.py", "--", $day, "1.0", "all") "$day\build"
$env:DAY17_DIR = $day; $out = "$SH\17_wrongside\v3\fullc"; New-Item -ItemType Directory -Force $out | Out-Null
Push-Location "$SH\17_wrongside\src"; python -E -s comp_s17.py "$SH\17_wrongside\v1\full" "$SH\17_wrongside\v1\full\bg.png" $out *> "$SH\17_wrongside\v3\comp.log"; Pop-Location
$env:DAY17_DIR = ""; Encode $out "$SH\17_wrongside\v3\17_wrongside_v3_silent.mp4"
Write-Host "produce_v3 done"
