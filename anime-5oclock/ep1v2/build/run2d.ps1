$env:NOTE_T='1.9'; $env:BLACK_T='2.6'
cd C:\Users\cross\Downloads\xc\anime-5oclock\ep1v2\build
foreach ($j in @(@('shot001',120,'fr001'),@('shot002',84,'fr002'),@('shot004',108,'fr004'),@('shot005',108,'fr005'))) {
  $p = Start-Process python -ArgumentList @('render.py',$j[0],$j[1],$j[2]) -NoNewWindow -PassThru -RedirectStandardOutput "log_$($j[0]).txt" -RedirectStandardError "log_$($j[0]).err"
  $p.PriorityClass='BelowNormal'; $p.WaitForExit(); "$($j[0]) exit $($p.ExitCode) frames $((ls $j[2]).Count)"
}
