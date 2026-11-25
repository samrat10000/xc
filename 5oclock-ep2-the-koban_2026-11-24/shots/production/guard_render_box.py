from pathlib import Path
p=Path(__file__).resolve().parent/'run_shot.ps1'
s=p.read_text(encoding='utf-8')
start=s.index('$deadline=[DateTime]')
end=s.index('python (Join-Path $PSScriptRoot \'finish_frames.py\')',start)
s=s[:start]+'''$deadline=[DateTime]::UtcNow.AddMinutes(45)
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
''' +s[end:]
p.write_text(s,encoding='utf-8')
