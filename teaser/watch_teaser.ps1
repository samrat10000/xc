# Live progress for the Night Terror teaser renders on this PC. Read-only: it only counts finished frames.
# Run: right-click this file > Run with PowerShell (close the window any time, the render keeps going).
$out = "C:\Users\cross\Downloads\xc\teaser\out"
$shots = [ordered]@{ '901_puddle_macro'=@(901,24); '902_tyre_cam'=@(902,36); '903_windshield_pov'=@(903,41); '904_camcorder'=@(904,34);
  '905_monster_pov'=@(905,29); '906_glass_rain'=@(906,14); '907_lightning'=@(907,10); '908_facade_fall'=@(908,19) }
$host.UI.RawUI.WindowTitle = 'Night Terror teaser - render progress'
while ($true) {
  Clear-Host
  Write-Host "NIGHT TERROR TEASER - renders on this PC    $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Red
  $done = 0; $all = 0
  foreach ($k in $shots.Keys) {
    $c, $n = $shots[$k]
    $have = @(Get-ChildItem "$out\c$c" -Filter f*.png -ErrorAction SilentlyContinue | ? Length -gt 0).Count
    if ($have -gt $n) { $have = $n }
    $done += $have; $all += $n
    $w = 30; $f = [int]($w * $have / $n)
    $bar = ('#' * $f).PadRight($w, '-')
    $col = if ($have -eq $n) { 'Green' } elseif ($have -gt 0) { 'Yellow' } else { 'DarkGray' }
    Write-Host ("{0,-20} [{1}] {2,3}/{3,-3}" -f $k, $bar, $have, $n) -ForegroundColor $col
  }
  $last = Get-Content "$out\progress.txt" -Tail 40 -ErrorAction SilentlyContinue | ? { $_ -match 'per_frame=' } | Select-Object -Last 1
  $pf = if ($last -match 'per_frame=([\d\.]+)') { [double]$matches[1] } else { 3 }
  $now = Get-Content "$out\progress.txt" -Tail 1 -ErrorAction SilentlyContinue
  $left = $all - $done; $eta = (Get-Date).AddMinutes($left * $pf)
  Write-Host "`nTotal $done / $all frames.  Last chunk: $pf min per frame.  About $([math]::Round($left*$pf/60,1)) h left (ETA $($eta.ToString('HH:mm')))." -ForegroundColor Cyan
  Write-Host "Now: $now" -ForegroundColor Gray
  Write-Progress -Activity 'Teaser renders on this PC' -Status "$done / $all frames" -PercentComplete ([int](100 * $done / $all))
  Start-Sleep -Seconds 20
}
