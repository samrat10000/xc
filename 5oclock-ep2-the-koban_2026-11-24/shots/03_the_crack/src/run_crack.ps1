param([string]$Blender = 'C:/Users/cross/Downloads/xc/blender501/blender.exe', [int]$Version = 1)
$ErrorActionPreference = 'Stop'
$shot = Split-Path -Parent $PSScriptRoot
$qa = Join-Path $shot 'qa'
$cel = Join-Path $qa "v${Version}_cel"
$frames = Join-Path $qa "v${Version}_frames"
$stem = "03_the_crack_v$Version"
$clip = Join-Path $shot "$stem.mp4"
if (Test-Path -LiteralPath $clip) { throw 'Choose a new version.' }
if (Get-Process blender -ErrorAction SilentlyContinue) { throw 'Another Blender instance is active.' }

python (Join-Path $PSScriptRoot 'paint_crack.py')
if ($LASTEXITCODE -ne 0) { throw 'Background paint failed.' }
python (Join-Path $PSScriptRoot 'place_canonical_crown.py')
if ($LASTEXITCODE -ne 0) { throw 'Crown preparation failed.' }
& $Blender -b -t 6 --factory-startup --python-exit-code 1 -P (Join-Path $PSScriptRoot 'build_crack.py') -- $cel 1.0 all 3
if ($LASTEXITCODE -ne 0) { throw 'Blender render failed.' }
python (Join-Path $PSScriptRoot 'comp_crack.py') $cel $frames 4
if ($LASTEXITCODE -ne 0) { throw 'Composite failed.' }

for ($i=1; $i -le 96; $i++) {
    if (!(Test-Path -LiteralPath (Join-Path $frames ('{0:000}.png' -f $i)))) { throw "Missing frame $i." }
}
ffmpeg -n -v error -framerate 24 -start_number 1 -i (Join-Path $frames '%03d.png') -frames:v 96 -an -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart $clip
if ($LASTEXITCODE -ne 0) { throw 'Encode failed.' }
foreach ($i in @(1,33,67,96)) {
    $index = '{0:000}' -f $i
    Copy-Item -LiteralPath (Join-Path $frames "$index.png") -Destination (Join-Path $shot "${stem}_f$index.png")
}
ffprobe -v error -count_frames -show_entries stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_read_frames,codec_type:format=duration -of json $clip
if ($LASTEXITCODE -ne 0) { throw 'Encode validation failed.' }

