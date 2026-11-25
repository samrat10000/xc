# Probe chain 2 (one waiter): 05c elbows, 09 band-follow, 17 closer camera, crowd sprites.
$ErrorActionPreference = "Continue"
$ep = Split-Path -Parent $PSScriptRoot; $pr = "$PSScriptRoot\probe.ps1"
& $pr -shot 05_ritual -frames "9,17,25" -name v3_probe_c2 -extra c
& $pr -shot 09_silence -frames "24,28,32" -name v2_probe3
& $pr -shot 17_wrongside -frames "1,13" -name v2_day_probe2 -build build_s17_day.py -comp none.py
$sp = "$ep\shots\11_mirror\crowd_sprites"; while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep 20 }
$q = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--factory-startup","--python","$ep\shots\11_mirror\src\build_crowd_sprites.py","--",$sp -PassThru -NoNewWindow -RedirectStandardOutput "$ep\shots\11_mirror\sprites.log" -RedirectStandardError "$ep\shots\11_mirror\sprites.err"; $q.PriorityClass = "BelowNormal"; $q.WaitForExit()
Write-Host "chain2 done"
