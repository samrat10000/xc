param(
    [string]$Blender = 'C:\Users\cross\Downloads\xc\blender501\blender.exe',
    [int]$Version = 1
)

$ErrorActionPreference = 'Stop'
$shot = Split-Path -Parent $PSScriptRoot
$render = Join-Path $shot "qa\v${Version}_cel"
$frames = Join-Path $shot "qa\v${Version}_frames"
$stem = "01_alarm_v$Version"
$clip = Join-Path $shot "$stem.mp4"
if (Test-Path -LiteralPath $clip) { throw "Clip already exists. Choose a fresh version." }

if (Get-Process blender -ErrorAction SilentlyContinue) {
    throw 'Blender is already running. Check that the priority render has finished.'
}
python (Join-Path $PSScriptRoot 'paint_alarm.py')
if ($LASTEXITCODE -ne 0) { throw 'Paint step failed.' }
& $Blender -b -t 6 --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'build_alarm.py') -- $render 1.0 all 3
if ($LASTEXITCODE -ne 0) { throw 'Blender render failed.' }
python (Join-Path $PSScriptRoot 'comp_alarm.py') $render $frames 3
if ($LASTEXITCODE -ne 0) { throw 'Composite failed.' }

$completed = @(1..72 | ForEach-Object { Test-Path -LiteralPath (Join-Path $frames ('{0:000}.png' -f $_)) })
if ($completed -contains $false) { throw 'One or more of the 72 frames are missing.' }
ffmpeg -n -v error -framerate 24 -start_number 1 -i (Join-Path $frames '%03d.png') -frames:v 72 -an -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -movflags +faststart $clip
if ($LASTEXITCODE -ne 0) { throw 'H.264 encode failed.' }
foreach ($number in @(1, 13, 33, 72)) {
    $index = '{0:000}' -f $number
    Copy-Item -LiteralPath (Join-Path $frames "$index.png") -Destination (Join-Path $shot "${stem}_f$index.png")
}
ffprobe -v error -count_frames -show_entries stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_read_frames,codec_type:format=duration -of json $clip
if ($LASTEXITCODE -ne 0) { throw 'Encode verification failed.' }
