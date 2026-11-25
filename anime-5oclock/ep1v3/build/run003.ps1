$p=Start-Process python -ArgumentList 'shot003.py','fr003' -WorkingDirectory $PSScriptRoot -NoNewWindow -PassThru
$p.PriorityClass='BelowNormal'; $p.WaitForExit()
ffmpeg -v error -n -framerate 24 -i "$PSScriptRoot\fr003\%04d.png" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart "$PSScriptRoot\..\003_sam_v3_silent.mp4"
