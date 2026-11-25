param()
$ErrorActionPreference='Stop'
$audio=Join-Path $PSScriptRoot 'audio'
$episode=Join-Path (Split-Path -Parent $PSScriptRoot) 'episode'
$cut=Join-Path $episode '5oclock_ep2_the_koban_silent_v1.mp4'
$final=Join-Path $episode '5oclock_ep2_the_koban_v1.mp4'
$voiceRuntime=Join-Path $audio 'runtime/Scripts/python.exe'
function Invoke-Stage([string]$Label,[scriptblock]$Action){
    Write-Host $Label
    & $Action
    if($LASTEXITCODE -ne 0){throw "$Label failed with exit code $LASTEXITCODE"}
}
Invoke-Stage 'Assembling verified silent shots' { python "$audio/assemble_episode.py" picture }
Invoke-Stage 'Checking frame order and authored black before voice production' { python "$PSScriptRoot/qa_reel.py" $cut }
Invoke-Stage 'Producing dialogue, recorded-instrument score and foley' { & $voiceRuntime "$audio/mix_episode.py" }
Invoke-Stage 'Mastering and muxing stereo audio' { python "$audio/assemble_episode.py" finish }
Invoke-Stage 'Verifying picture after audio mux' { python "$PSScriptRoot/qa_reel.py" $final }
Invoke-Stage 'Writing the reel and shot delivery index' { python "$PSScriptRoot/delivery_index.py" }
