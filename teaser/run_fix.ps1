# Teaser fix pass: 903 giant, 906 glass, 907 Brute, 908 slab re-lit, fog ON; 12-frame chunks, output teaser\out_v2
$ErrorActionPreference = 'Continue'
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[W.P]::SetThreadExecutionState([uint32]"0x80000001") | Out-Null
$blender = "C:\Users\cross\Downloads\xc\blender501\blender.exe"
$out = "C:\Users\cross\Downloads\xc\teaser\out_v2"
New-Item -ItemType Directory -Force $out | Out-Null
Get-ChildItem "$out\c*" -Filter *.png -Recurse -ErrorAction SilentlyContinue | ? Length -eq 0 | Remove-Item
Remove-Item Env:NOFOG -ErrorAction SilentlyContinue
Set-Location "C:\Users\cross\Downloads\xc\ep1"
$env:DEVICE = 'GPU'; $env:OUTROOT = $out; $env:SAMP = '20'; $env:LIGHTPATHS = '1'; $env:NOPERSIST = '1'
$env:RES = '.75'
foreach ($job in @(@(903,41), @(906,14), @(907,10), @(908,19))) {
  $cut = $job[0]; $n = $job[1]; $env:CUT = "$cut"
  for ($a = 1; $a -le $n; $a += 12) {
    $b = [math]::Min($a + 11, $n)
    $todo = @($a..$b | ? { -not (Test-Path ("$out\c$cut\f{0:D4}.png" -f $_)) })
    if ($todo.Count -eq 0) { continue }
    $env:FR = "$a,$b"; $t0 = Get-Date
    "$(Get-Date -Format s) START $cut f$a-$b ($($todo.Count) to render)" | Add-Content "$out\progress.txt"
    & $blender -b -P teaser.py *>> "$out\log_$cut.txt"
    $min = [math]::Round(((Get-Date)-$t0).TotalMinutes,2)
    "$(Get-Date -Format s) END $cut f$a-$b exit=$LASTEXITCODE wall=${min}min per_frame=$([math]::Round($min/$todo.Count,2))min" | Add-Content "$out\progress.txt"
  }
}
"finished $(Get-Date -Format s)" | Set-Content "$out\DONE_fix.txt"
[W.P]::SetThreadExecutionState([uint32]"0x80000000") | Out-Null
