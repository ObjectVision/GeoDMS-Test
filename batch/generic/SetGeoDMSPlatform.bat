Rem Bepaal de folder waarin programma's voor Win32 worden geinstalleerd.
Set ProgramFiles32=%ProgramFiles(x86)%
Set GeoDmsPlatform=x64

if "%ProgramFiles(x86)%"=="" (
	Set ProgramFiles32=%ProgramFiles%
	Set GeoDmsPlatform=Win32
)

Rem Verwerk de meegegeven parameter die bepaalt welke exe getest moet worden
Set GeoDmsPath=%ProgramFiles%\ObjectVision\GeoDms%1%
IF %1 == D32 Set GeoDmsPath=%geodms_rootdir%\bin\Debug\Win32
IF %1 == R32 Set GeoDmsPath=%geodms_rootdir%\bin\Release\Win32
IF %1 == D64 Set GeoDmsPath=%geodms_rootdir%\bin\Debug\x64
IF %1 == R64 Set GeoDmsPath=%geodms_rootdir%\bin\Release\x64

Set GeoDmsRunPath=%GeoDmsPath%\GeoDmsRun.exe
Set GeoDmsGuiPath=%GeoDmsPath%\GeoDmsGui.exe
Set GeoDmsImGuiPath=%GeoDmsPath%\GeoDmsImGui.exe
Set GeoDmsCallerPath=%GeoDmsPath%\GeoDmsCaller.exe

IF %1 == D64 Set GeoDmsPlatform=x64
IF %1 == R64 Set GeoDmsPlatform=x64
IF %1 == D32 Set GeoDmsPlatform=Win32
IF %1 == R32 Set GeoDmsPlatform=Win32

Echo Testing %GeoDMSRunPath%
Echo.