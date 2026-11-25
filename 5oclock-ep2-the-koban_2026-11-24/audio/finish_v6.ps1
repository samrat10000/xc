$ErrorActionPreference='Stop'
function RunStage([string]$Name,[scriptblock]$Action){
    Write-Host $Name
    & $Action
    if($LASTEXITCODE -ne 0){throw "$Name failed"}
}
RunStage 'Locking the v6 picture edit' { python "$PSScriptRoot/revision_cut_v6.py" }
RunStage 'Mixing the original speech takes and new music cues' { python "$PSScriptRoot/revision_mix_v6.py" }
RunStage 'Checking decoded release boundaries and dialogue times' { python "$PSScriptRoot/v6_check_release.py" }
RunStage 'Writing the verified delivery index' { python "$PSScriptRoot/v6_delivery.py" }
