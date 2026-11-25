# shot 05 full render: 3 cuts x 28 f, joined into one 84-frame clip. Below-normal priority. Refuses to overwrite.
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot; $v = (Resolve-Path "$src\..").Path + "\v1"; $all = "$v\fullc"
if (Test-Path $all) { throw "v1\fullc exists: bump the version" }
New-Item -ItemType Directory -Force $all | Out-Null
$t0 = Get-Date; $n = 0
foreach ($cut in "a", "b", "c") {
  $full = "$v\full_$cut"; New-Item -ItemType Directory -Force $full | Out-Null
  $p = Start-Process "c:\Users\cross\Downloads\xc\blender501\blender.exe" -ArgumentList "-b","--python","$src\build_s05.py","--","$full","1.0","all",$cut -PassThru -NoNewWindow -RedirectStandardOutput "$full\build.log" -RedirectStandardError "$full\build.err"
  $p.PriorityClass = "BelowNormal"; $p.WaitForExit()
  Push-Location $full; python -I "$src\paint_bg04.py" "$full\meta.json" *> "$full\paint.log"; Pop-Location
  $q = Start-Process python -ArgumentList "-I","$src\comp_s05.py","$full","$full\c" -PassThru -NoNewWindow -RedirectStandardOutput "$full\comp.log" -RedirectStandardError "$full\comp.err"
  $q.PriorityClass = "BelowNormal"; $q.WaitForExit()
  foreach ($f in 1..28) { $n++; Copy-Item ("$full\c\{0:D3}.png" -f $f) ("$all\{0:D3}.png" -f $n) }
  "cut $cut done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$v\timing.txt" -Append
}
ffmpeg -y -loglevel error -framerate 24 -i "$all\%03d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$v\05_ritual_v1_silent.mp4"
"encode done " + [int]((Get-Date)-$t0).TotalSeconds | Out-File "$v\timing.txt" -Append