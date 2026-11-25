param([int]$Version = 3)
$ErrorActionPreference='Stop'
$project=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$audio=Join-Path $project 'audio'
$episode=Join-Path $project 'episode'
$cut=Join-Path $episode '5oclock_ep2_the_koban_silent_v1.mp4'
function Invoke-Stage([string]$Label,[scriptblock]$Action){
    Write-Host $Label
    & $Action
    if($LASTEXITCODE -ne 0){throw "$Label failed with exit code $LASTEXITCODE"}
}
Invoke-Stage 'Assembling verified silent shots' { python "$audio/assemble_episode.py" picture }
Invoke-Stage 'Checking frame order and authored black before audio' { python "$PSScriptRoot/qa_reel.py" $cut }
Invoke-Stage 'Scoring and mixing the locked picture' { python "$audio/mix_episode.py" }
Invoke-Stage 'Mastering and muxing stereo audio' { python "$audio/assemble_episode.py" finish $Version }
$takes=Get-Content "$audio/audio_timeline.json" -Raw | ConvertFrom-Json
$label=if($takes.missing_takes.Count){"score_only_v$Version"}else{"v$Version"}
$final=Join-Path $episode "5oclock_ep2_the_koban_${label}.mp4"
Invoke-Stage 'Verifying picture after audio mux' { python "$PSScriptRoot/qa_reel.py" $final }
Invoke-Stage 'Writing the reel and shot delivery index' { python "$PSScriptRoot/delivery_index.py" $Version }
