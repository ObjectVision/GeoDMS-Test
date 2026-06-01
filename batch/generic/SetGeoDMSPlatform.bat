Rem Bepaal de folder waarin programma's voor Win32 worden geinstalleerd.
Set ProgramFiles32=%ProgramFiles(x86)%
Set GeoDmsPlatform=x64

if "%ProgramFiles(x86)%"=="" (
	Set ProgramFiles32=%ProgramFiles%
	Set GeoDmsPlatform=Win32
)

if ("%geodms_rootdir%") EQU ("") Set geodms_rootdir=C:\dev\GeoDMS

Rem %1 = version selector. %2 = flavor suffix (m / c / l). The flavor is
Rem only meaningful for the installed-build case below (line 13); the
Rem dev-tree shortcuts (D32/R32/D64/R64/CD64/CR64) overwrite GeoDmsPath
Rem after that, so a flavor passed alongside a dev-tree shortcut is
Rem harmlessly discarded.
IF "%2"=="" (
    Set GeoDmsPath=%ProgramFiles%\ObjectVision\GeoDms%1
) ELSE (
    Set GeoDmsPath=%ProgramFiles%\ObjectVision\GeoDms%1.%2
)
IF %1 == D32  Set GeoDmsPath=%geodms_rootdir%\bin\Debug\Win32
IF %1 == R32  Set GeoDmsPath=%geodms_rootdir%\bin\Release\Win32
IF %1 == D64  Set GeoDmsPath=%geodms_rootdir%\bin\Debug\x64
IF %1 == R64  Set GeoDmsPath=%geodms_rootdir%\bin\Release\x64
IF %1 == CD64 Set GeoDmsPath=%geodms_rootdir%\build\windows-x64-debug\bin
IF %1 == CR64 Set GeoDmsPath=%geodms_rootdir%\build\windows-x64-release\bin

Set GeoDmsRunPath=%GeoDmsPath%\GeoDmsRun.exe
Set GeoDmsGuiPath=%GeoDmsPath%\GeoDmsGuiQt.exe
Set GeoDmsGuiQtPath=%GeoDmsPath%\GeoDmsGuiQt.exe
Set GeoDmsCallerPath=%GeoDmsPath%\GeoDmsCaller.exe

IF %1 == D64 Set GeoDmsPlatform=x64
IF %1 == R64 Set GeoDmsPlatform=x64
IF %1 == CD64 Set GeoDmsPlatform=x64
IF %1 == CR64 Set GeoDmsPlatform=x64
IF %1 == D32 Set GeoDmsPlatform=Win32
IF %1 == R32 Set GeoDmsPlatform=Win32

Echo Testing %GeoDMSRunPath%
Echo.