param(
    [Parameter(Mandatory=$true)][string]$Shot,
    [ValidateSet('Probe','Native','Master')][string]$Mode = 'Probe',
    [int]$Pass = 1,
    [int]$Version = 1,
    [string]$Frames,
    [switch]$Resume,
    [string]$Blender = 'C:/Users/cross/Downloads/xc/blender501/blender.exe'
)
$ErrorActionPreference='Stop'
$plan=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'shots.json') | ConvertFrom-Json -AsHashtable
$card=$plan[$Shot]
$crackV6=$Shot -eq '03' -and $env:KOBAN_PICTURE_REVISION -eq '6'
if($crackV6){$card=@{slug='the_crack';scene='crack';frames=96;keys=@(1,29,46,63,74,96);stills=@(1,33,67,96)}}
if(!$card){throw "Unknown shot $Shot"}
if($env:KOBAN_PICTURE_REVISION -in @('6','7')){
    if($Shot -eq '07'){$card.frames=128; $card.keys=@(1,18,35,61,87,128); $card.stills=@(1,19,68,128)}
    if($Shot -eq '15'){$card.frames=96; $card.keys=@(1,18,34,52,75,96); $card.stills=@(1,32,60,96)}
}
$project=Split-Path -Parent $PSScriptRoot
$guide='C:/Users/cross/.codex/skills/motion2d/scripts/qa_frames.py'
$dest=Join-Path $project "${Shot}_$($card.slug)"
New-Item -ItemType Directory -Force -Path "$dest/qa","$dest/src" | Out-Null
$tag=if($Mode -eq 'Master'){"v$Version"} elseif($Mode -eq 'Native'){"native$Pass"} else{"p$Pass"}
$cel=Join-Path $dest "qa/${tag}_cel"
$framesOut=Join-Path $dest "qa/${tag}_frames"
$review=Join-Path $dest "qa/${tag}_review"
$base="${Shot}_$($card.slug)_v$Version"
$mp4=Join-Path $dest "$base.mp4"
if(($Mode -eq 'Master') -and (Test-Path -LiteralPath $mp4)){throw 'Published master already exists.'}
if($Resume -and $Mode -ne 'Master'){throw 'Resume applies only to an interrupted master.'}
if($Resume){
    python (Join-Path $PSScriptRoot 'verify_partial.py') $cel
    if($LASTEXITCODE -ne 0){throw 'Could not verify the interrupted cels.'}
}
$keys=if($Resume){'resume'}elseif($Mode -eq 'Master'){'all'}elseif($Frames){$Frames}else{$card.keys -join ','}
$scale=if($Mode -eq 'Probe'){'0.50'}else{'1.0'}
$deadline=[DateTime]::UtcNow.AddMinutes(45)
$log=Join-Path $dest "qa/${tag}_render.log"
$blenderScript=Join-Path $PSScriptRoot 'build_reel.py'
$attempt=0
do{
    while(Get-Process blender -ErrorAction SilentlyContinue){
        if([DateTime]::UtcNow -gt $deadline){throw 'The GPU is still in use by another Blender render.'}
        Start-Sleep -Seconds 3
    }
    $attempt++
    $attemptLog=if($attempt -eq 1){$log}else{"$log.retry$attempt"}
    $launchArgs=@('-b','-t','6','--factory-startup','--python-exit-code','1','-P',"`"$blenderScript`"",'--',$Shot,"`"$cel`"",$scale,$keys)
    if($crackV6){
        $shotScript=Join-Path $dest 'src/build_crack_v6.py'
        $launchArgs=@('-b','-t','6','--factory-startup','--python-exit-code','1','-P',"`"$shotScript`"",'--',"`"$cel`"",$scale,$keys,'4')
    }
    $render=Start-Process -FilePath $Blender -ArgumentList $launchArgs -RedirectStandardOutput $attemptLog -RedirectStandardError "$attemptLog.stderr" -WindowStyle Hidden -PassThru
    try {$render.PriorityClass='BelowNormal'} catch {Write-Verbose 'Blender exited before priority could be set.'}
    $preempted=$false
    while(!$render.WaitForExit(1500)){
        $other=Get-Process blender -ErrorAction SilentlyContinue | Where-Object Id -ne $render.Id
        if($other){
            if(!$render.HasExited){
                $render.Kill()
                $render.WaitForExit()
                $preempted=$true
                Write-Host "Episode 2 shot $Shot yielded the GPU to an outside Blender process."
            }
            break
        }
    }
    if($preempted -and $Mode -eq 'Master'){
        python (Join-Path $PSScriptRoot 'verify_partial.py') $cel
        if($LASTEXITCODE -ne 0){throw 'Interrupted cels could not be verified.'}
        $keys='resume'
    }
}while($preempted -and [DateTime]::UtcNow -lt $deadline)
if($render.ExitCode -ne 0){
    Get-Content -Tail 25 -LiteralPath $attemptLog,"$attemptLog.stderr"
    throw "Blender failed in shot $Shot"
}
if($crackV6){
    python (Join-Path $dest 'src/comp_crack.py') $cel $framesOut 4
}else{
    python (Join-Path $PSScriptRoot 'finish_frames.py') $cel $framesOut $Shot
}
if($LASTEXITCODE -ne 0){throw "Composite failed in shot $Shot"}
$reference=Join-Path $project '02_wrong_room/02_wrong_room_v2_f039.png'
$qaArgs=@($guide,$framesOut,'--ref',$reference,'--n',$(if($Mode -eq 'Master'){12}else{6}),'--out',$review)
if($Mode -eq 'Master'){
    $n=[int]$card.frames
    if((Get-ChildItem -LiteralPath $framesOut -Filter '*.png').Count -ne $n){throw "Wrong frame count in $Shot"}
    ffmpeg -n -v error -framerate 24 -start_number 1 -i (Join-Path $framesOut '%03d.png') -frames:v $n -an -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart $mp4
    if($LASTEXITCODE -ne 0){throw "Encode failed in shot $Shot"}
    foreach($number in $card.stills){
        $f='{0:000}' -f $number
        Copy-Item -LiteralPath (Join-Path $framesOut "$f.png") -Destination (Join-Path $dest "${base}_f$f.png")
    }
    $crop=Join-Path $dest 'qa/crops.json'
    if(Test-Path -LiteralPath $crop){$qaArgs+=@('--crops',$crop)}
    ffprobe -v error -count_frames -show_entries stream=codec_type,codec_name,nb_read_frames,width,height,r_frame_rate:format=duration -of json $mp4
    $sourceName=if($env:KOBAN_PICTURE_REVISION -in @('6','7')){"SOURCE_v$Version.md"}else{'SOURCE.md'}
    $recipe=if($env:KOBAN_PICTURE_REVISION -eq '7'){'../production/motion_v7.py'}elseif($crackV6){'build_crack_v6.py'}elseif($env:KOBAN_PICTURE_REVISION -eq '6'){"../production/$($card.scene)_v6.py"}else{"../production/$($card.scene).py"}
    @" 
Shared scene source: $recipe
Render entry point: ../production/run_shot.ps1 -Shot $Shot -Mode Master -Version $Version
Production card and frame timing: ../production/shots.json
"@ | Set-Content -LiteralPath (Join-Path $dest "src/$sourceName")
}
python @qaArgs
if($LASTEXITCODE -ne 0){throw "Contact sheet failed in shot $Shot"}

