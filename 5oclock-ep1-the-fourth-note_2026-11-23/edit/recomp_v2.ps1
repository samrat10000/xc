# Recomp 11-14 (3D crowd) and 17 (3D mother) from their v1 cels. No GPU. python -E -s, NOT -I: -I drops the script's folder
# from sys.path and the comps import their sibling modules (paint_night11, paint_day17) - K8.
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $SH = "$ep\shots"
$env:NIGHT_SPRITES = "$SH\11_mirror\crowd_sprites"
function Encode($dir, $mp4) { ffmpeg -y -loglevel error -framerate 24 -i "$dir\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $mp4; Write-Host "encoded $(Split-Path $mp4 -Leaf) frames=$((Get-ChildItem $dir -Filter *.png).Count)" }
foreach ($shot in '11_mirror', '12_closer', '13_mirrorsam', '14_fourth') {
  $n = $shot.Substring(0, 2); $full = "$SH\$shot\v1\full"; $out = "$SH\$shot\v2\fullc"
  Remove-Item "$out\*.png" -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force $out | Out-Null; Push-Location "$SH\$shot\src"
  if ($n -eq '14') { python -E -s ecu_s14.py $full $out *> "$SH\$shot\v2\ecu.log" }
  python -E -s "comp_s$n.py" $full "$full\bg.png" $out *> "$SH\$shot\v2\comp.log"; Pop-Location
  Encode $out "$SH\$shot\v2\${shot}_v2_silent.mp4"
}
$env:DAY17_DIR = "$SH\17_wrongside\v2\day"; $out = "$SH\17_wrongside\v2\fullc"; New-Item -ItemType Directory -Force $out | Out-Null
Push-Location "$SH\17_wrongside\src"; python -E -s comp_s17.py "$SH\17_wrongside\v1\full" "$SH\17_wrongside\v1\full\bg.png" $out *> "$SH\17_wrongside\v2\comp.log"; Pop-Location
Encode $out "$SH\17_wrongside\v2\17_wrongside_v2_silent.mp4"
Write-Host "recomp done"
