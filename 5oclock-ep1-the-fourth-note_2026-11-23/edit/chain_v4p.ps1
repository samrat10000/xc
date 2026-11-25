# v4 probes (half res): 08 (sky + snap + pouring water), 10 (water, hand), 10b (headphones, wire), 12 (street), 14 (ECU), 17 (mom arms)
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $SH = "$ep\shots"; $B = "c:\Users\cross\Downloads\xc\blender501\blender.exe"; $p = "$PSScriptRoot\probe.ps1"
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"; $env:SET_FWD = "1"; $env:GRIP_V3 = "1"; $env:NIGHT_SPRITES = "$SH\11_mirror\crowd_sprites"
function RB($argl, $dir) { while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 3 }; $q = Start-Process $B -ArgumentList $argl -PassThru -NoNewWindow -RedirectStandardOutput "$dir\build.log" -RedirectStandardError "$dir\build.err"; $q.PriorityClass = "BelowNormal"; $q.WaitForExit() }

$q4 = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\b3u73gzzc.output"; while (-not (Select-String -Path $q4 -Pattern "chain v4q done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 5 }

foreach ($s in @(@('12_closer', '30,40'), @('14_fourth', '12,24,37'))) {
  $shot = $s[0]; $n = $shot.Substring(0, 2); $src = "$SH\$shot\src"; $full = "$SH\$shot\v3_probe\full"; Remove-Item "$full\*" -Recurse -Force -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force "$full\fullc" | Out-Null
  RB @("-b", "--python", "$src\build_s$n.py", "--", $full, "0.5", $s[1]) $full
  $m = Get-Content "$full\meta.json" -Raw | ConvertFrom-Json; $k = ($m.PSObject.Properties | Select-Object -Last 1).Value
  Push-Location $src; python -E -s paint_bg.py "$full\bg.png" $k.sx $k.sy *> "$full\paint.log"
  if ($n -eq '14') { python -E -s ecu_s14.py $full "$full\fullc" *> "$full\ecu.log" }
  python -E -s "comp_s$n.py" $full "$full\bg.png" "$full\fullc" *> "$full\comp.log"; Pop-Location
  Write-Host "$shot probe done"
}
$day = "$SH\17_wrongside\v4_probe\day"; New-Item -ItemType Directory -Force $day | Out-Null
RB @("-b", "--python", "$SH\17_wrongside\src\build_s17_day.py", "--", $day, "1.0", "30") $day
Write-Host "chain v4p done"




