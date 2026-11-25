# 5 O'CLOCK Ep1 "The Fourth Note" - silent picture assembly (G6). Hard cuts in story order, no crossfades. Checks the frame count (1512 = 63.0 s).
$ErrorActionPreference = "Stop"
$ep = Split-Path -Parent $PSScriptRoot; $s = "$ep\shots"; $ed = $PSScriptRoot
$order = @(
  "01_speaker\v4\01_speaker_v4.mp4", "02_mirror\v1\02_mirror_v1.mp4", "03_kiriyama\v2\03_kiriyama_v2.mp4", "04_ride\v4\04_ride_v4.mp4",
  "05_ritual\v3\05_ritual_v3_silent.mp4", "06_phone\v1\06_phone_v1_silent.mp4", "07_notes\v1\07_notes_v1_silent.mp4", "08_frozen\v2\08_frozen_v2_silent.mp4",
  "09_silence\v2\09_silence_v2_silent.mp4", "10_eyes\v2\10_eyes_v2_silent.mp4", "11_mirror\v2\11_mirror_v2_silent.mp4", "12_closer\v2\12_closer_v2_silent.mp4",
  "13_mirrorsam\v2\13_mirrorsam_v2_silent.mp4", "14_fourth\v2\14_fourth_v2_silent.mp4", "15_listener\v3\15_listener_v3_silent.mp4", "16_welcome\v2\16_welcome_v2_silent.mp4",
  "17_wrongside\v2\17_wrongside_v2_silent.mp4", "18_rule7\v1\18_rule7_v1_silent.mp4")                                   # v2 cut: Sam's v1 notes
$list = "$ed\concat.txt"; $lines = @()
foreach ($c in $order) { $p = "$s\$c"; if (-not (Test-Path $p)) { throw "missing $c" }; $lines += "file '" + $p.Replace("'", "'\''") + "'" }
[IO.File]::WriteAllLines($list, $lines)
$v = 1; while (Test-Path "$ed\5oclock_ep1_v${v}_silent.mp4") { $v++ }                     # never overwrite a version
$out = "$ed\5oclock_ep1_v${v}_silent.mp4"
ffmpeg -y -loglevel error -f concat -safe 0 -i $list -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -r 24 $out
ffmpeg -y -loglevel error -i $out -vf scale=720:1280 -c:v libx264 -crf 21 -preset medium -pix_fmt yuv420p "$ed\5oclock_ep1_v${v}_silent_phone.mp4"
$n = ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $out
"frames: $n (expected 1512)" | Tee-Object -FilePath "$ed\assemble_v$v.log"
# one frame per shot (the middle frame) as a storyboard check sheet
$py = @"
import subprocess, os
from PIL import Image
ed = r'$ed'; out = r'$out'; starts = [0, 72, 144, 228, 324, 408, 456, 564, 684, 756, 840, 924, 1008, 1080, 1164, 1272, 1344, 1416, 1512]
sh = Image.new('RGB', (9 * 160, 2 * 284))
for i in range(18):
    m = (starts[i] + starts[i + 1]) // 2; p = os.path.join(ed, 'tmp_%02d.png' % i)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-vf', 'select=eq(n\\,%d)' % m, '-vframes', '1', p])
    sh.paste(Image.open(p).resize((160, 284)), ((i % 9) * 160, (i // 9) * 284)); os.remove(p)
sh.save(os.path.join(ed, 'storyboard_check_v$v.png'))
"@
[IO.File]::WriteAllText("$ed\storyboard_check.py", $py, (New-Object Text.UTF8Encoding $false)); python -I "$ed\storyboard_check.py"   # K1: never inline python in PowerShell
"done: $out"
