# after chain v3f: re-probe 15 (ember mouths) and 17 (calling funnel)
$d = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\buulz61cn.output"
while (-not (Select-String -Path $d -Pattern "chain v3f done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 5 }
$SH = (Split-Path -Parent $PSScriptRoot) + "\shots"
& "$SH\15_listener\src\run_v4.ps1" -name v4_probe2 -frames "70,100" -scale 0.5
$day = "$SH\17_wrongside\v3_probe2\day"; New-Item -ItemType Directory -Force $day | Out-Null
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 3 }
$env:SET_EXT = "1"; $env:SET_FWD = "1"; $env:GRIP_V3 = "1"; $env:GLASS_INTERIOR = "0.22"
$q = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$SH\17_wrongside\src\build_s17_day.py","--",$day,"1.0","30" -PassThru -NoNewWindow -RedirectStandardOutput "$day\build.log" -RedirectStandardError "$day\build.err"
$q.PriorityClass = "BelowNormal"; $q.WaitForExit()
Write-Host "chain v3g done"
