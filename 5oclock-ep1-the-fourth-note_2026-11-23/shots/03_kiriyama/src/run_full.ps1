# Windows version of run_full.sh. Runs Blender and Python at below-normal priority (the teaser has priority on this PC).
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$B = 'C:\Users\cross\Downloads\xc\blender501\blender.exe'
function Low($exe, $argList, $log) {
  $p = Start-Process $exe -ArgumentList $argList -NoNewWindow -PassThru -RedirectStandardOutput $log -RedirectStandardError "$log.err"
  $null = $p.Handle; $p.PriorityClass = 'BelowNormal'; $p.WaitForExit()   # Handle caches the exit code
  if ($p.ExitCode -ne 0) { throw "$exe failed, see $log.err" }
}
Remove-Item full, fullc -Recurse -Force -ErrorAction SilentlyContinue
Low $B @('-b', '--python', 'build_s03.py', '--', "$PSScriptRoot\full", '1.0', 'all') full_build.log
Low python @('paint_bg03.py', 'full\meta.json') full_paint.log   # makes sky03.png and mts03.png (not in the repo)
Low python @('comp_s03.py', 'full', 'fullc') full_comp.log
ffmpeg -y -loglevel error -framerate 24 -i fullc/%03d.png -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p 03_kiriyama_v2.mp4
if ($LASTEXITCODE -eq 0) { 'DONE' }
