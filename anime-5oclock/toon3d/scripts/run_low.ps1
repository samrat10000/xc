param([string]$Script,[string]$Log,[Parameter(ValueFromRemainingArguments=$true)]$Rest)
$a=@('-b','-P',$Script); if ($Rest) { $a += @('--')+$Rest }
$p=Start-Process -FilePath C:\Users\cross\Downloads\xc\blender501\blender.exe -ArgumentList $a -NoNewWindow -PassThru -RedirectStandardOutput $Log -RedirectStandardError "$Log.err"
$p.PriorityClass='BelowNormal'; $p.WaitForExit()
