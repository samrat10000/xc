# One chain (H3: never two waiters): after the 16 v2 render, probe 17-day, 05a, 05c, 09 in order. Each probe waits for a free Blender.
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $pr = "$PSScriptRoot\probe.ps1"
while (-not (Test-Path "$ep\shots\16_welcome\v2\16_welcome_v2_silent.mp4")) { Start-Sleep 30 }
Start-Sleep 5
& $pr -shot 17_wrongside -frames "1,9,13,25" -name v2_day_probe -build build_s17_day.py -comp none.py
& $pr -shot 05_ritual -frames "9,15,21,25,27" -name v3_probe_a -extra a
& $pr -shot 05_ritual -frames "1,9,17,25" -name v3_probe_c -extra c
& $pr -shot 09_silence -frames "20,26,32" -name v2_probe2
$sp = "$ep\shots\11_mirror\crowd_sprites"; while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 20 }
$q = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--factory-startup","--python","$ep\shots\11_mirror\src\build_crowd_sprites.py","--",$sp -PassThru -NoNewWindow -RedirectStandardOutput "$ep\shots\11_mirror\sprites.log" -RedirectStandardError "$ep\shots\11_mirror\sprites.err"; $q.PriorityClass = "BelowNormal"; $q.WaitForExit()
Write-Host "chain done"
