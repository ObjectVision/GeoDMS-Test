<#
.SYNOPSIS
    Launch a GeoDMS regression run as a DETACHED, session-independent Windows
    process, so it survives terminal close, agent-session cleanup, and long
    durations (multi-hour runs).

.WHY
    A run started as a child of an interactive shell or an automation/agent
    session is killed when that session is cleaned up (observed: the whole
    python + wsl-bridge + GeoDmsRun tree dies at once, with NO error and the
    GeoDMS log cut off mid-line -- looks like a crash but is not). Start-Process
    detaches the run from the launching shell's lifetime, so it keeps running.

.NOTES
    Linux (.l) runs: WSL2 must have its swap re-allocated after every Windows
    reboot. Run `wsl --shutdown` once, then a `wsl -d Ubuntu -- free -h` to boot
    it fresh so the .wslconfig swap (D:\WSL\swap.vhdx, 304 GB) is active before
    starting. GUI tests (t1630/t1640/t1642) pass on .l (the executable bundles its
    own Qt); off by default, pass -LinuxGui to include them.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File batch\run_detached.ps1 -Version 20.1.0.l
    powershell -ExecutionPolicy Bypass -File batch\run_detached.ps1 -Version 20.1.0.m -Tests t641
#>
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$Tests = "",
    [switch]$NoGui,
    [switch]$LinuxGui,
    [string]$ResultsBase = "C:\LocalData\GeoDMS_Test_Results"
)

$batch = $PSScriptRoot
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$tag   = $Version -replace '[^0-9A-Za-z]', '_'
# Detached-run logs (.out/.err/.pid) are scratch -> keep them in _Temp, not beside results.
$tmpDir = Join-Path $ResultsBase "_Temp"
if (-not (Test-Path $tmpDir)) { New-Item -ItemType Directory -Force $tmpDir | Out-Null }
$out   = Join-Path $tmpDir "run_${tag}_$stamp.out"
$err   = Join-Path $tmpDir "run_${tag}_$stamp.err"
$pidf  = Join-Path $tmpDir "run_${tag}.pid"

# Pin the interpreter: bare "python" resolves via PATH (C:\Python314 on this box),
# but the harness is maintained against 3.13 -- use the py launcher to select it.
$pyArgs = @("-3.13", "full.py", "-version", $Version)
if ($Tests) { $pyArgs += @("-tests", $Tests) }
if ($NoGui) { $pyArgs += "-no-gui" }
if ($LinuxGui) { $pyArgs += "-linux-gui" }

$proc = Start-Process -FilePath "py" -ArgumentList $pyArgs -WorkingDirectory $batch `
            -RedirectStandardOutput $out -RedirectStandardError $err -WindowStyle Hidden -PassThru
$proc.Id | Out-File $pidf -Encoding ascii

Write-Host "Detached GeoDMS run started."
Write-Host "  version : $Version$(if ($Tests) { "  (tests: $Tests)" })"
Write-Host "  PID     : $($proc.Id)   (saved to $pidf)"
Write-Host "  stdout  : $out"
Write-Host "  stderr  : $err"
Write-Host ""
Write-Host "Watch progress : Get-Content '$out' -Wait | Select-String 'Running experiment'"
Write-Host "Check alive    : Get-Process -Id $($proc.Id) -ErrorAction SilentlyContinue"
Write-Host "Stop the run   : Stop-Process -Id $($proc.Id)"
