$ErrorActionPreference = 'Continue'
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[W.P]::SetThreadExecutionState(0x80000001) | Out-Null   # ES_CONTINUOUS|ES_SYSTEM_REQUIRED
$ff = 'C:\Users\cross\AppData\Local\Microsoft\WinGet\Packages\yt-dlp.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-N-121938-g2456a39581-win64-gpl\bin\ffmpeg.exe'
$out = 'C:\Users\cross\Downloads\xc\ep1pc\out\v7final'
$repo = 'C:\Users\cross\Downloads\xc\ep1patch'
New-Item -ItemType Directory -Force $out | Out-Null
$cuts = [ordered]@{ '125'='125_brute_block_v2_silent.mp4'; '140'='140_stalker_cu_v1_silent.mp4'; '150'='150_stalker_v1_silent.mp4' }
Set-Location C:\Users\cross\Downloads\xc\ep1pc\ep1
foreach ($c in $cuts.Keys) {
  while (tasklist | findstr /i blender.exe) { Start-Sleep 20 }
  $env:CUT=$c; $env:RES='1'; $env:SAMP='48'; $env:DEVICE='GPU'; $env:MB='.2'; $env:STEP='1'; $env:OUTROOT=$out
  Remove-Item Env:FR -ErrorAction SilentlyContinue
  $t = Get-Date
  & C:\Users\cross\Downloads\xc\blender501\blender.exe -b --python shots2.py *> "$out\r$c.log"
  $sec = ((Get-Date) - $t).TotalSeconds
  $n = @(Get-ChildItem "$out\c$c\*.png" -ErrorAction SilentlyContinue).Count
  $err = (Select-String -Path "$out\r$c.log" -Pattern 'Traceback|Error' -SimpleMatch:$false | Select-Object -First 1).Line
  "CUT $c frames=$n secs=$([int]$sec) spf=$(if($n){[math]::Round($sec/$n,1)}else{'-'}) err=$err"
  if ($n -eq 0) { "FAILED $c"; Get-Content "$out\r$c.log" -Tail 40; continue }
  $mp4 = "$out\$($cuts[$c])"
  & $ff -y -loglevel error -framerate 24 -i "$out\c$c\f%04d.png" -vf scale=1080:1920 -c:v libx264 -crf 14 -pix_fmt yuv420p -an $mp4
  "MP4 $c $(Test-Path $mp4)"
}
[W.P]::SetThreadExecutionState(0x80000000) | Out-Null
"QUEUE DONE"
