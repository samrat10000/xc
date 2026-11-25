# 5 O'CLOCK Ep1 v3 cut (Sam's v2 notes): new shot 10b (48 f) after 10; 11 and 12 lose their first 24 f (12 no longer opens on the
# back of Sam's head), so the episode stays 1512 f = 63.0 s and every audio cue keeps its time. Never overwrites a version.
$ErrorActionPreference = "Stop"
$ep = Split-Path -Parent $PSScriptRoot; $s = "$ep\shots"; $ed = $PSScriptRoot; $tmp = "$ed\v3_tmp"; New-Item -ItemType Directory -Force $tmp | Out-Null
function Trim24($src, $dst) { ffmpeg -y -loglevel error -i $src -vf "trim=start_frame=24,setpts=PTS-STARTPTS" -c:v libx264 -crf 12 -preset slow -pix_fmt yuv420p $dst; $dst }
$t11 = Trim24 "$s\11_mirror\v2\11_mirror_v2_silent.mp4" "$tmp\11_trim.mp4"
$t12 = Trim24 "$s\12_closer\v2\12_closer_v2_silent.mp4" "$tmp\12_trim.mp4"
$order = @(
  "$s\01_speaker\v4\01_speaker_v4.mp4", "$s\02_mirror\v1\02_mirror_v1.mp4", "$s\03_kiriyama\v2\03_kiriyama_v2.mp4", "$s\04_ride\v5\04_ride_v5_silent.mp4",
  "$s\05_ritual\v4\05_ritual_v4_silent.mp4", "$s\06_phone\v1\06_phone_v1_silent.mp4", "$s\07_notes\v1\07_notes_v1_silent.mp4", "$s\08_frozen\v4\08_frozen_v4_silent.mp4",
  "$s\09_silence\v3\09_silence_v3_silent.mp4", "$s\10_eyes\v2\10_eyes_v2_silent.mp4", "$s\10b_arrive\v3\10b_arrive_v3_silent.mp4", $t11, $t12,
  "$s\13_mirrorsam\v2\13_mirrorsam_v2_silent.mp4", "$s\14_fourth\v2\14_fourth_v2_silent.mp4", "$s\15_listener\v4\15_listener_v4_silent.mp4", "$s\16_welcome\v2\16_welcome_v2_silent.mp4",
  "$s\17_wrongside\v3\17_wrongside_v3_silent.mp4", "$s\18_rule7\v2\18_rule7_v2_silent.mp4")
$lines = @(); foreach ($p in $order) { if (-not (Test-Path $p)) { throw "missing $p" }; $lines += "file '" + $p.Replace("'", "'\''") + "'" }
[IO.File]::WriteAllLines("$ed\concat_v3.txt", $lines)
$v = 1; while (Test-Path "$ed\5oclock_ep1_v${v}_silent.mp4") { $v++ }
$out = "$ed\5oclock_ep1_v${v}_silent.mp4"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$ed\concat_v3.txt" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -r 24 $out
$n = ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $out
"frames: $n (expected 1512)" | Tee-Object -FilePath "$ed\assemble_v$v.log"
$fin = "$ed\5oclock_ep1_v$v.mp4"
ffmpeg -y -loglevel error -i $out -i "$ep\audio\stems\premaster.wav" -map 0:v -map 1:a -c:v copy -af "loudnorm=I=-15:TP=-1.5:LRA=11,alimiter=limit=0.84" -ar 48000 -c:a aac -b:a 256k -shortest -movflags +faststart $fin
ffmpeg -y -loglevel error -i $fin -c:v libvpx-vp9 -b:v 6M -deadline realtime -cpu-used 8 -row-mt 1 -c:a libopus -b:a 192k "$ed\5oclock_ep1_v${v}_preview.webm"
"done: $fin"



