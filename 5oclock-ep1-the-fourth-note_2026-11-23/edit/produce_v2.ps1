# Ep1 v2 production chain (one waiter; one Blender at a time, below-normal; waits whenever Codex's Blender runs).
# Order: crowd sprites -> recomp 11-14 (no GPU) -> 17 day pass + recomp -> 05 v3 (3 cuts) -> 08 v2 -> 09 v2 -> 10 v2.
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $SH = "$ep\shots"; $B = "c:\Users\cross\Downloads\xc\blender501\blender.exe"
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"; $env:NIGHT_SPRITES = "$SH\11_mirror\crowd_sprites"
function Wait-Free { while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 30 } }
function Run-Blender($argl, $log) { Wait-Free; $p = Start-Process $B -ArgumentList $argl -PassThru -NoNewWindow -RedirectStandardOutput "$log.log" -RedirectStandardError "$log.err"; $p.PriorityClass = "BelowNormal"; $p.WaitForExit() }
function Encode($dir, $mp4) { ffmpeg -y -loglevel error -framerate 24 -i "$dir\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $mp4; Write-Host "encoded $mp4 frames=$((Get-ChildItem $dir -Filter *.png).Count)" }
function Log($m) { Write-Host "$(Get-Date -Format HH:mm) $m" }

# 1. crowd sprites (rest-pose stances, no apron board)
Remove-Item "$SH\11_mirror\crowd_sprites\*" -Force -ErrorAction SilentlyContinue   # K7: $s and $S are the SAME variable in PowerShell
Run-Blender @("-b", "--factory-startup", "--python", "$SH\11_mirror\src\build_crowd_sprites.py", "--", "$SH\11_mirror\crowd_sprites") "$SH\11_mirror\sprites"; Log "sprites done $((Get-ChildItem "$SH\11_mirror\crowd_sprites" -Filter *.png).Count)"

# 2. recomp 11-14 from their v1 cels with the 3D crowd (comp only)
foreach ($s in '11_mirror', '12_closer', '13_mirrorsam', '14_fourth') {
  $n = $s.Substring(0, 2); $src = "$SH\$s\src"; $full = "$SH\$s\v1\full"; $out = "$SH\$s\v2\fullc"
  New-Item -ItemType Directory -Force $out | Out-Null; Push-Location $src
  if ($n -eq '14') { python -I ecu_s14.py $full $out *> "$SH\$s\v2\ecu.log" }
  python -I "comp_s$n.py" $full "$full\bg.png" $out *> "$SH\$s\v2\comp.log"; Pop-Location
  Encode $out "$SH\$s\v2\${s}_v2_silent.mp4"; Log "$s recomp done"
}

# 3. shot 17: the 3D day insert, then recomp from v1 cels
$day = "$SH\17_wrongside\v2\day"; New-Item -ItemType Directory -Force $day | Out-Null
Run-Blender @("-b", "--python", "$SH\17_wrongside\src\build_s17_day.py", "--", $day, "1.0", "all") "$day\build"
$env:DAY17_DIR = $day; $out = "$SH\17_wrongside\v2\fullc"; New-Item -ItemType Directory -Force $out | Out-Null
Push-Location "$SH\17_wrongside\src"; python -I comp_s17.py "$SH\17_wrongside\v1\full" "$SH\17_wrongside\v1\full\bg.png" $out *> "$SH\17_wrongside\v2\comp.log"; Pop-Location
$env:DAY17_DIR = ""; Encode $out "$SH\17_wrongside\v2\17_wrongside_v2_silent.mp4"; Log "17 done"

# 4. shot 05 v3: three cuts x 28 f
$v = "$SH\05_ritual\v3"; $all = "$v\fullc"; New-Item -ItemType Directory -Force $all | Out-Null; $k = 0
foreach ($cut in 'a', 'b', 'c') {
  $full = "$v\full_$cut"; New-Item -ItemType Directory -Force $full | Out-Null
  Run-Blender @("-b", "--python", "$SH\05_ritual\src\build_s05.py", "--", $full, "1.0", "all", $cut) "$full\build"
  Push-Location $full; python -I "$SH\05_ritual\src\paint_bg04.py" "$full\meta.json" *> "$full\paint.log"; Pop-Location
  python -I "$SH\05_ritual\src\comp_s05.py" $full "$full\c" *> "$full\comp.log"
  foreach ($f in 1..28) { $k++; Copy-Item ("$full\c\{0:D3}.png" -f $f) ("$all\{0:D3}.png" -f $k) }
}
Encode $all "$v\05_ritual_v3_silent.mp4"; Log "05 done"

# 5. shots 08, 09, 10 v2
foreach ($s in '08_frozen', '09_silence', '10_eyes') {
  $n = $s.Substring(0, 2); $src = "$SH\$s\src"; $vd = "$SH\$s\v2"; $full = "$vd\full"; New-Item -ItemType Directory -Force $full | Out-Null
  Run-Blender @("-b", "--python", "$src\build_s$n.py", "--", $full, "1.0", "all") "$full\build"
  $ps = if (Test-Path "$src\paint_bg04.py") { "$src\paint_bg04.py" } else { "$SH\04_ride\src\paint_bg04.py" }
  Push-Location $full; python -I $ps "$full\meta.json" *> "$full\paint.log"; Pop-Location
  python -I "$src\comp_s$n.py" $full "$full\fullc" *> "$full\comp.log"
  Encode "$full\fullc" "$vd\${s}_v2_silent.mp4"; Log "$s done"
}
Log "produce_v2 done"
