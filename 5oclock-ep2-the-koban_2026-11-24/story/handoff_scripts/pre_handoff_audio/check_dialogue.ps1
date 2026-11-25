param([Parameter(Mandatory=$true)][string]$Master)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$timeline=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'audio_timeline.json') | ConvertFrom-Json
$recognizer=New-Object System.Speech.Recognition.SpeechRecognitionEngine
$recognizer.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
$qa=Join-Path $PSScriptRoot 'qa'
New-Item -ItemType Directory -Path $qa -Force | Out-Null
$lines=foreach($i in 0..($timeline.dialogue.Length-1)){
    $line=$timeline.dialogue[$i]
    $file=Join-Path $qa ('mix_line_{0:00}.wav' -f ($i+1))
    $start=[Math]::Round($line.start-.13,3).ToString([CultureInfo]::InvariantCulture)
    $len=[Math]::Round($line.end-$line.start+.33,3).ToString([CultureInfo]::InvariantCulture)
    & ffmpeg -y -v error -ss $start -i $Master -t $len -ac 1 -ar 16000 -c:a pcm_s16le $file
    if($LASTEXITCODE -ne 0){throw "Couldn't extract $file"}
    $recognizer.SetInputToWaveFile($file)
    $result=$recognizer.Recognize()
    $recognized=if($result){$result.Text}else{''}
    $confidence=if($result){[Math]::Round($result.Confidence,3)}else{0}
    [pscustomobject]@{Role=$line.role; Start=$line.start; Expected=$line.text; Recognized=$recognized; Confidence=$confidence}
}
$recognizer.Dispose()
$lines | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $qa 'dialogue_recognition.json')
$lines | Format-Table Role,Start,Recognized,Confidence -AutoSize
