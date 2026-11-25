param(
    [string]$Blender = 'C:/Users/cross/Downloads/xc/blender501/blender.exe',
    [int]$Version = 1
)
$ErrorActionPreference = 'Stop'
$shot = Split-Path -Parent $PSScriptRoot
$qa = Join-Path $shot 'qa'
$cel = Join-Path $qa "v${Version}_cel"
$frames = Join-Path $qa "v${Version}_frames"
$stem = "02_wrong_room_v$Version"
$clip = Join-Path $shot "$stem.mp4"
if (Test-Path -LiteralPath $clip) { throw 'This master already exists. Increment the version.' }
if (Get-Process blender -ErrorAction SilentlyContinue) { throw 'Another Blender instance is active.' }
python (Join-Path $PSScriptRoot 'paint_room.py')
if ($LASTEXITCODE -ne 0) { throw 'Paint failed.' }
& $Blender -b -t 6 --factory-startup --python-exit-code 1 -P (Join-Path $PSScriptRoot 'build_wrong_room.py') -- $cel 1.0 all 3
if ($LASTEXITCODE -ne 0) { throw 'Blender failed.' }
python (Join-Path $PSScriptRoot 'comp_wrong_room.py') $cel $frames 3
if ($LASTEXITCODE -ne 0) { throw 'Composite failed.' }
for ($n=1; $n -le 96; $n++) {
    if (!(Test-Path -LiteralPath (Join-Path $frames ('{0:000}.png' -f $n)))) { throw "Composite frame $n is missing." }
}
ffmpeg -n -v error -framerate 24 -start_number 1 -i (Join-Path $frames '%03d.png') -frames:v 96 -an -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart $clip
if ($LASTEXITCODE -ne 0) { throw 'Encode failed.' }
foreach ($n in @(1,39,63,96)) {
    $frame='{0:000}' -f $n
    Copy-Item -LiteralPath (Join-Path $frames "$frame.png") -Destination (Join-Path $shot "${stem}_f$frame.png")
}
ffprobe -v error -count_frames -show_entries stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_read_frames,codec_type:format=duration -of json $clip
if ($LASTEXITCODE -ne 0) { throw 'Encode validation failed.' }


