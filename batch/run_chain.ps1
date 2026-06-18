<#
.SYNOPSIS
    Run a regression suite for several GeoDMS versions in sequence, each as a
    full `full.py -version <v>` run, logging per version. Meant to be launched
    DETACHED (Start-Process) so a multi-version overnight chain survives session
    teardown. Each run uses the committed per-test timeout caps.
.EXAMPLE
    Start-Process powershell -ArgumentList '-ExecutionPolicy','Bypass','-File',
      'batch\run_chain.ps1' -WindowStyle Hidden
#>
param(
    [string[]]$Versions = @("20.1.0.m", "19.0.0"),
    [string]$Tests = "",
    [string]$ResultsBase = "C:\LocalData\GeoDMS_Test_Results"
)
# Accept -Versions as either a real array or a single comma-separated string.
$Versions = @($Versions | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$batch  = $PSScriptRoot
$tmpDir = Join-Path $ResultsBase "_Temp"
if (-not (Test-Path $tmpDir)) { New-Item -ItemType Directory -Force $tmpDir | Out-Null }
$prog   = Join-Path $tmpDir "run_chain_progress.log"
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] CHAIN START: $($Versions -join ', ')$(if ($Tests) { "  (tests: $Tests)" })" | Out-File -Append -Encoding utf8 $prog

foreach ($v in $Versions) {
    $tag   = $v -replace '[^0-9A-Za-z]', '_'
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $out   = Join-Path $tmpDir "run_${tag}_$stamp.out"
    $err   = Join-Path $tmpDir "run_${tag}_$stamp.err"
    $pyArgs = @("full.py", "-version", $v)
    if ($Tests) { $pyArgs += @("-tests", $Tests) }
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] START $v -> $(Split-Path $out -Leaf)" | Out-File -Append -Encoding utf8 $prog
    $p = Start-Process python -ArgumentList $pyArgs `
            -WorkingDirectory $batch -RedirectStandardOutput $out -RedirectStandardError $err `
            -WindowStyle Hidden -PassThru
    $p.WaitForExit()
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] END   $v exit=$($p.ExitCode)" | Out-File -Append -Encoding utf8 $prog
}
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] CHAIN COMPLETE" | Out-File -Append -Encoding utf8 $prog
