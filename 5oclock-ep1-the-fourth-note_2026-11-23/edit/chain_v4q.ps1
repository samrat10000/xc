# after chain v4p: re-probe 10 (leaf corridor cleared)
$d = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\bh54pf4l1.output"
while (-not (Select-String -Path $d -Pattern "chain v4p done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 5 }
& "$PSScriptRoot\probe.ps1" -shot 10_eyes -frames "10,40,70" -name v4_probe
Write-Host "chain v4q done"
