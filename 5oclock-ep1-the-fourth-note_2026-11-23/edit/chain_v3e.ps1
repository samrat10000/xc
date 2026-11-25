# after chain v3d: re-probe 05a with the travelling-target reach (the v4 probe ran on the old code)
$d = "C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\27982df2-ef1a-4763-bbb6-eba3167e1b86\tasks\bcw8fiykw.output"
while (-not (Select-String -Path $d -Pattern "chain v3d done" -Quiet -ErrorAction SilentlyContinue)) { Start-Sleep 5 }
& "$PSScriptRoot\probe.ps1" -shot 05_ritual -frames "5,9,13,17,21,25,30" -name v5_probe_a -extra a
Write-Host "chain v3e done"
