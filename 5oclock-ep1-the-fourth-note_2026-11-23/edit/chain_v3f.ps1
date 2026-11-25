# after chain v3e: re-probe 10b (bike placed from the shoulder)
$d = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\bvygkp5k3.output"
while (-not (Select-String -Path $d -Pattern "chain v3e done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 5 }
$sh = Split-Path -Parent $PSScriptRoot
& "$sh\shots\10b_arrive\src\run_10b.ps1" -name v4_probe -frames "1,30,48" -scale 0.5
Write-Host "chain v3f done"
