# v3 probe chain 1 (one waiter, H3): 08 world extension, 05a mirror push, 05c shutter.
$p = "$PSScriptRoot\probe.ps1"
& $p -shot 08_frozen -frames "40,62,84,106,120" -name v3_probe
& $p -shot 05_ritual -frames "9,15,19,23,27,33" -name v3_probe_a -extra a
& $p -shot 05_ritual -frames "2,8,14,20,26" -name v3_probe_c -extra c
& $p -shot 09_silence -frames "14,20,26,30,48" -name v3_probe
Write-Host "chain v3a done"

