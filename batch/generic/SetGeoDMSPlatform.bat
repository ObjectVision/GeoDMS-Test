Rem Bepaal de folder waarin programma's voor Win32 worden geinstalleerd.
Set ProgramFiles32=%ProgramFiles(x86)%
Set GeoDmsPlatform=x64

if "%ProgramFiles(x86)%"=="" (
	Set ProgramFiles32=%ProgramFiles%
	Set GeoDmsPlatform=Win32
)

if ("%geodms_rootdir%") EQU ("") Set geodms_rootdir=C:\dev\GeoDMS

Rem %1 = version selector. %2 = flavor suffix (m / c / g / l). The flavor names
Rem the installed dir in the general case below; the dev-tree shortcuts
Rem (D32/R32/D64/R64/CD64/CR64/GD64/GR64) overwrite GeoDmsPath after that. It
Rem still reaches the tests as GeoDmsFlavor (unit_flagged.bat), which is why the
Rem GLOBIO shortcuts GD64/GR64 are run with flavor g.
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
IF %1 == GD64 Set GeoDmsPath=%geodms_rootdir%\bin_GLOBIO\Debug\x64
IF %1 == GR64 Set GeoDmsPath=%geodms_rootdir%\bin_GLOBIO\Release\x64

Set GeoDmsRunPath=%GeoDmsPath%\GeoDmsRun.exe
Set GeoDmsGuiPath=%GeoDmsPath%\GeoDmsGuiQt.exe
Set GeoDmsGuiQtPath=%GeoDmsPath%\GeoDmsGuiQt.exe
Set GeoDmsCallerPath=%GeoDmsPath%\GeoDmsCaller.exe

IF %1 == D64 Set GeoDmsPlatform=x64
IF %1 == R64 Set GeoDmsPlatform=x64
IF %1 == CD64 Set GeoDmsPlatform=x64
IF %1 == CR64 Set GeoDmsPlatform=x64
IF %1 == GD64 Set GeoDmsPlatform=x64
IF %1 == GR64 Set GeoDmsPlatform=x64
IF %1 == D32 Set GeoDmsPlatform=Win32
IF %1 == R32 Set GeoDmsPlatform=Win32

Echo Testing %GeoDMSRunPath%
Echo.