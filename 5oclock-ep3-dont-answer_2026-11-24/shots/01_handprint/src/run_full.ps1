$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$B = 'C:\Users\cross\Downloads\xc\blender501\blender.exe'
$EP3 = 'C:\Users\cross\Downloads\xc\5oclock-ep3-dont-answer_2026-11-24'
$OUT = "$PSScriptRoot\full"
$OUTC = "$PSScriptRoot\fullc"
$V1 = "$EP3\shots\01_handprint\v1"

while (Get-Process -Name blender -ErrorAction SilentlyContinue) {
  Write-Host 'Waiting for running Blender GPU job...'
  Start-Sleep -Seconds 5
}

function RunLow($exe, $argList, $log) {
  $p = Start-Process $exe -ArgumentList $argList -NoNewWindow -PassThru -RedirectStandardOutput $log -RedirectStandardError "$log.err"
  $null = $p.Handle
  $p.PriorityClass = 'BelowNormal'
  $p.WaitForExit()
  if ($p.ExitCode -ne 0) { throw "$exe failed ($($p.ExitCode)), see $log.err" }
}

Remove-Item $OUT, $OUTC -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OUT, $OUTC, $V1 | Out-Null

RunLow python @('make_textures.py') "$PSScriptRoot\full_tex.log"
RunLow $B @('-b', '--python', 'build_s01.py', '--', $OUT, '1.0', 'all') "$PSScriptRoot\full_build.log"
RunLow python @('paint_bg01.py', "$OUT\meta.json", "$PSScriptRoot\bg_full.png") "$PSScriptRoot\full_paint.log"
RunLow python @('comp_s01.py', $OUT, "$PSScriptRoot\bg_full.png", "$OUT\meta.json", $OUTC) "$PSScriptRoot\full_comp.log"

$MP4 = "$V1\01_handprint_v1.mp4"
ffmpeg -y -loglevel error -framerate 24 -i "$OUTC\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $MP4
if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed" }
Write-Host "DONE $MP4"
