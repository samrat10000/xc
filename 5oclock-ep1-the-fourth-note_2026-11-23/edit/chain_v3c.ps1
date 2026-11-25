# v3 probe chain 3: after chain 2, shot 04 with the glass flicker fix + new grip + forward world (frames around 11-12 s).
$b = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\bhzyr5u4p.output"
while (-not (Select-String -Path $b -Pattern "chain v3b done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 5 }
& "$PSScriptRoot\probe.ps1" -shot 04_ride -frames "30,36,42,48,54,60,66" -name v5_probe
Write-Host "chain v3c done"
