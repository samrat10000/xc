# after the 08 v4 re-render: 10b v2 (free arm tucked in)
$T = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\buawuuoin.output"
while (-not (Select-String -Path $T -Pattern "08 v4 done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 10 }
$SH = (Split-Path -Parent $PSScriptRoot) + "\shots"
& "$SH\10b_arrive\src\run_10b.ps1" -name v2 -frames all -scale 1.0
Write-Host "10b v2 done"
