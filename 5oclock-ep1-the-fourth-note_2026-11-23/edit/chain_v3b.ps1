# v3 probe chain 2: waits for chain 1 to finish (one GPU waiter at a time, H3), then 09, 10b, 15 v4, 17 day probes.
$ep = Split-Path -Parent $PSScriptRoot; $SH = "$ep\shots"
$a = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\b9kar5l3n.output"
while (-not (Select-String -Path $a -Pattern "chain v3a done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 5 }
& "$PSScriptRoot\probe.ps1" -shot 09_silence -frames "14,20,26,30,48" -name v3_probe
& "$SH\10b_arrive\src\run_10b.ps1" -name v3_probe -frames "1,16,30,48" -scale 0.5
& "$SH\15_listener\src\run_v4.ps1" -name v4_probe -frames "40,70,85,100" -scale 0.5
$day = "$SH\17_wrongside\v3_probe\day"; New-Item -ItemType Directory -Force $day | Out-Null
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 3 }
$env:GLASS_INTERIOR = "0.22"; $env:SET_EXT = "1"; $env:SET_FWD = "1"; $env:GRIP_V3 = "1"
$p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$SH\17_wrongside\src\build_s17_day.py","--",$day,"0.5","12,30,50" -PassThru -NoNewWindow -RedirectStandardOutput "$day\build.log" -RedirectStandardError "$day\build.err"
$p.PriorityClass = "BelowNormal"; $p.WaitForExit()
Write-Host "chain v3b done"
