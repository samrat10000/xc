# Teaser 911 v2 (bull skull, body motion, new skid): frames 73-139 on this PC, 6-frame chunks, output teaser\out_v2
$ErrorActionPreference = 'Continue'
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[W.P]::SetThreadExecutionState([uint32]"0x80000001") | Out-Null
$blender = "C:\Users\cross\Downloads\xc\blender501\blender.exe"
$out = "C:\Users\cross\Downloads\xc\teaser\out_v2"
New-Item -ItemType Directory -Force $out | Out-Null
Get-ChildItem "$out\c*" -Filter *.png -Recurse -ErrorAction SilentlyContinue | ? Length -eq 0 | Remove-Item
Set-Location "C:\Users\cross\Downloads\xc\ep1"
$env:DEVICE = 'GPU'; $env:OUTROOT = $out; $env:SAMP = '20'; $env:NOFOG = '1'; $env:LIGHTPATHS = '1'; $env:NOPERSIST = '1'
$env:CUT = '911'; $env:RES = '.75'
for ($a = 73; $a -le 139; $a += 6) {
  $b = [math]::Min($a + 5, 139)
  $todo = @($a..$b | ? { -not (Test-Path ("$out\c911\f{0:D4}.png" -f $_)) })
  if ($todo.Count -eq 0) { continue }
  $env:FR = "$a,$b"; $t0 = Get-Date
  "$(Get-Date -Format s) START 911 f$a-$b ($($todo.Count) to render)" | Add-Content "$out\progress.txt"
  & $blender -b -P teaser.py *>> "$out\log_911.txt"
  $min = [math]::Round(((Get-Date)-$t0).TotalMinutes,2)
  "$(Get-Date -Format s) END 911 f$a-$b exit=$LASTEXITCODE wall=${min}min per_frame=$([math]::Round($min/$todo.Count,2))min" | Add-Content "$out\progress.txt"
}
"finished $(Get-Date -Format s)" | Set-Content "$out\DONE.txt"
[W.P]::SetThreadExecutionState([uint32]"0x80000000") | Out-Null
