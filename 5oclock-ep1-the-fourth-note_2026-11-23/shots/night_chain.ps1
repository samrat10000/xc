# night chain: 05 v2, then 02 and 03 from their approved code. Each step logs; a failure does not stop the next.
$ep = "c:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\shots"
$log = "$ep\night_chain.log"
"start " + (Get-Date) | Out-File $log
try { powershell -ExecutionPolicy Bypass -File "$ep\05_ritual\src\run_full_v2.ps1"; "05 v2 done " + (Get-Date) | Out-File $log -Append } catch { "05 FAILED $_" | Out-File $log -Append }
foreach ($s in "02_mirror", "03_kiriyama") {
  try { powershell -ExecutionPolicy Bypass -File "$ep\$s\src\run_full.ps1" *> "$ep\$s\src\run.log"; "$s done " + (Get-Date) | Out-File $log -Append } catch { "$s FAILED $_" | Out-File $log -Append }
}
"end " + (Get-Date) | Out-File $log -Append