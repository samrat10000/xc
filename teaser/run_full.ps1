# Night Terror teaser - full render batch. Rerun to resume (existing frames are skipped).
# Each cut renders in chunks of 6 frames, one Blender process per chunk, so GPU/RAM resets every chunk.
# While it runs it asks Windows not to idle-sleep (SetThreadExecutionState); no power settings are changed.
$ErrorActionPreference = 'Continue'
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[W.P]::SetThreadExecutionState([uint32]"0x80000001") | Out-Null   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
$blender = "C:\Users\cross\Downloads\xc\blender501\blender.exe"
$out = "C:\Users\cross\Downloads\xc\teaser\out"
New-Item -ItemType Directory -Force $out | Out-Null
Remove-Item "$out\DONE.txt" -ErrorAction SilentlyContinue
# a 0-byte PNG is a placeholder from an interrupted frame; remove so it re-renders
Get-ChildItem "$out\c*" -Filter *.png -Recurse -ErrorAction SilentlyContinue | ? Length -eq 0 | Remove-Item
Set-Location "C:\Users\cross\Downloads\xc\ep1"
$env:DEVICE = 'GPU'; $env:OUTROOT = $out
$env:SAMP = '20'; $env:NOFOG = '1'; $env:LIGHTPATHS = '1'; $env:NOPERSIST = '1'
$nf = @{911=139; 910=48; 909=19; 912=4; 901=24; 902=36; 903=41; 904=34; 905=29; 906=14; 907=10; 908=19}
$chunk = 6
foreach ($c in 911,910,909,912,901,902,903,904,905,906,907,908) {
  $env:CUT = "$c"
  if ($c -eq 911) { $env:RES = '.75' } else { $env:RES = '.667' }
  for ($a = 1; $a -le $nf[$c]; $a += $chunk) {
    $b = [math]::Min($a + $chunk - 1, $nf[$c])
    $todo = @($a..$b | ? { -not (Test-Path ("$out\c$c\f{0:D4}.png" -f $_)) })
    if ($todo.Count -eq 0) { continue }
    $env:FR = "$a,$b"
    $t0 = Get-Date
    "$(Get-Date -Format s) START $c f$a-$b ($($todo.Count) to render)" | Add-Content "$out\progress.txt"
    & $blender -b -P teaser.py *>> "$out\log_$c.txt"
    $min = [math]::Round(((Get-Date)-$t0).TotalMinutes,2)
    "$(Get-Date -Format s) END $c f$a-$b exit=$LASTEXITCODE wall=${min}min per_frame=$([math]::Round($min/$todo.Count,2))min" | Add-Content "$out\progress.txt"
  }
}
"finished $(Get-Date -Format s)" | Set-Content "$out\DONE.txt"
[W.P]::SetThreadExecutionState([uint32]"0x80000000") | Out-Null
