# Move the newest ElevenLabs downloads into audio/ as <prefix>_take<letters> (oldest of the batch = first letter).
# usage: take_in.ps1 -prefix N1 -letters AB   (expects exactly that many new files since the last call)
param([string]$prefix, [string]$letters = "AB")
$dl = "C:\Users\cross\Downloads"; $au = $PSScriptRoot; $stamp = "$au\.take_stamp"
$since = if (Test-Path $stamp) { (Get-Item $stamp).LastWriteTime } else { (Get-Date).AddMinutes(-30) }
$new = Get-ChildItem $dl -Filter "ElevenLabs_*.mp3" | ? { $_.LastWriteTime -gt $since } | Sort-Object LastWriteTime
if ($new.Count -ne $letters.Length) { Write-Host "expected $($letters.Length) new files, found $($new.Count): $($new.Name -join ', ')"; exit 1 }
for ($i = 0; $i -lt $new.Count; $i++) { $dst = "$au\${prefix}_take$($letters[$i]).mp3"; Move-Item $new[$i].FullName $dst -Force; Write-Host "$($new[$i].Name) -> $(Split-Path $dst -Leaf)" }
Set-Content $stamp (Get-Date) ; (Get-Item $stamp).LastWriteTime = Get-Date
