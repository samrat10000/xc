# Temporary keep-awake: holds a system+display wake request until xfer_hq\PUSHED.txt exists or 4 h pass. Changes no settings.
Add-Type -Namespace KA -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
$flag = "C:\Users\cross\Downloads\xc\teaser\xfer_hq\PUSHED.txt"
$end = (Get-Date).AddHours(4)
[KA.P]::SetThreadExecutionState([uint32]"0x80000003") | Out-Null
while (-not (Test-Path $flag) -and (Get-Date) -lt $end) { Start-Sleep -Seconds 60 }
[KA.P]::SetThreadExecutionState([uint32]"0x80000000") | Out-Null
