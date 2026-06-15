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
    [string]$ResultsBase = "C:\LocalData\GeoDMS-Test\Regression"
)
$batch = $PSScriptRoot
$prog  = Join-Path $ResultsBase "run_chain_progress.log"
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] CHAIN START: $($Versions -join ', ')" | Out-File -Append -Encoding utf8 $prog

foreach ($v in $Versions) {
    $tag   = $v -replace '[^0-9A-Za-z]', '_'
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $out   = Join-Path $ResultsBase "run_${tag}_$stamp.out"
    $err   = Join-Path $ResultsBase "run_${tag}_$stamp.err"
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] START $v -> $(Split-Path $out -Leaf)" | Out-File -Append -Encoding utf8 $prog
    $p = Start-Process python -ArgumentList "full.py", "-version", $v `
            -WorkingDirectory $batch -RedirectStandardOutput $out -RedirectStandardError $err `
            -WindowStyle Hidden -PassThru
    $p.WaitForExit()
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] END   $v exit=$($p.ExitCode)" | Out-File -Append -Encoding utf8 $prog
}
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] CHAIN COMPLETE" | Out-File -Append -Encoding utf8 $prog
