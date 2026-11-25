param(
    [Parameter(Mandatory=$true)][string]$Shot,
    [ValidateSet('Probe','Native','Master')][string]$Mode = 'Probe',
    [int]$Pass = 1,
    [int]$Version = 1,
    [string]$Frames,
    [string]$Blender = 'C:/Users/cross/Downloads/xc/blender501/blender.exe'
)
$ErrorActionPreference='Stop'
$plan=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'shots.json') | ConvertFrom-Json -AsHashtable
$card=$plan[$Shot]
if(!$card){throw "Unknown shot $Shot"}
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
$keys=if($Mode -eq 'Master'){'all'}elseif($Frames){$Frames}else{$card.keys -join ','}
$scale=if($Mode -eq 'Probe'){'0.43'}else{'1.0'}
$deadline=[DateTime]::UtcNow.AddMinutes(22)
while(Get-Process blender -ErrorAction SilentlyContinue){
    if([DateTime]::UtcNow -gt $deadline){throw 'The GPU is still in use by another Blender render.'}
    Start-Sleep -Seconds 3
}
$log=Join-Path $dest "qa/${tag}_render.log"
& $Blender -b -t 6 --factory-startup --python-exit-code 1 -P (Join-Path $PSScriptRoot 'build_reel.py') -- $Shot $cel $scale $keys *> $log
if($LASTEXITCODE -ne 0){Get-Content -Tail 30 -LiteralPath $log;throw "Blender failed in shot $Shot"}
python (Join-Path $PSScriptRoot 'finish_frames.py') $cel $framesOut $Shot
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
    @" 
Shared scene source: ../production/$($card.scene).py
Render entry point: ../production/run_shot.ps1 -Shot $Shot -Mode Master -Version $Version
Production card and frame timing: ../production/shots.json
"@ | Set-Content -LiteralPath (Join-Path $dest 'src/SOURCE.md')
}
python @qaArgs
if($LASTEXITCODE -ne 0){throw "Contact sheet failed in shot $Shot"}

