Rem Bepaal de folder waarin programma's voor Win32 worden geinstalleerd.
Set ProgramFiles32=%ProgramFiles(x86)%
Set GeoDmsPlatform=x64

if "%ProgramFiles(x86)%"=="" (
	Set ProgramFiles32=%ProgramFiles%
	Set GeoDmsPlatform=Win32
)

if ("%geodms_rootdir%") EQU ("") Set geodms_rootdir=C:\dev\GeoDMS

Rem Verwerk de meegegeven parameter die bepaalt welke exe getest moet worden
Set GeoDmsPath=%ProgramFiles%\ObjectVision\GeoDms%1%
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