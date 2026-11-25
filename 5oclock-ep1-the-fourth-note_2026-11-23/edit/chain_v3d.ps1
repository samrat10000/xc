# v3 probe chain (single waiter, H3; keeps going past a failed step). Fresh folder names (stale cels crashed a comp, K15).
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $SH = "$ep\shots"; $p = "$PSScriptRoot\probe.ps1"
& $p -shot 05_ritual -frames "9,15,19,23,27,33" -name v4_probe_a -extra a
& $p -shot 05_ritual -frames "2,8,14,20,26" -name v4_probe_c -extra c
& $p -shot 09_silence -frames "14,20,26,30,48" -name v3_probe
& "$SH\10b_arrive\src\run_10b.ps1" -name v3_probe -frames "1,16,30,48" -scale 0.5
& "$SH\15_listener\src\run_v4.ps1" -name v4_probe -frames "40,70,85,100" -scale 0.5
$day = "$SH\17_wrongside\v3_probe\day"; New-Item -ItemType Directory -Force $day | Out-Null
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 3 }
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"; $env:SET_FWD = "1"; $env:GRIP_V3 = "1"
$q = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$SH\17_wrongside\src\build_s17_day.py","--",$day,"0.5","12,30,50" -PassThru -NoNewWindow -RedirectStandardOutput "$day\build.log" -RedirectStandardError "$day\build.err"
$q.PriorityClass = "BelowNormal"; $q.WaitForExit(); Write-Host "17 day probe done"
& $p -shot 04_ride -frames "30,36,42,48,54,60,66" -name v5_probe
& $p -shot 08_frozen -frames "62,84,120" -name v3_probe2
Write-Host "chain v3d done"
