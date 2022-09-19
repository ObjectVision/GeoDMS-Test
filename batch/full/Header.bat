Rem Algemene Informatie over de versie, OS, Computer weggeschreven en in gebruik voor Header van de test
FOR /F "tokens=2*" %%A IN ('REG QUERY "HKEY_CURRENT_USER\Control Panel\International" /v sShortDate 2^>NUL') DO SET DATEFORMAT=%%B

Rem  Schrijf informatie over de computer uit het register weg naar de LogFileDir
SET STATUSFLAGS=%1%2

Rem deze informatie moet eerst weggeschreven worden omdat die de version key bepaalt.  
Echo !COMPUTERNAME! > %LogFileDir%\computername.txt
Echo !DATEFORMAT!   > %LogFileDir%\date_format.txt
Echo !STATUSFLAGS!  > %LogFileDir%\statusflags.txt

SETLOCAL EnableDelayedExpansion
rem bepaal Operating System
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%version%" == "10.0" Set OS=Windows 10
if "%version%" == "6.3" Set OS=Windows 8.1
if "%version%" == "6.2" Set OS=Windows 8
if "%version%" == "6.1" Set OS=Windows 7
if "%version%" == "6.0" Set OS=Windows Vista.

Echo.
Echo MakeVersionInfo with GeoDMS Command: %GeoDmsRunCmdBaseLarge% %RegressionPath% results/VersionInfo/all

%GeoDmsRunCmdBaseLarge% %RegressionPath% results/VersionInfo/all >> %GeoDmsLogFilePath%

set /p ver_key=<%LogFileDir%/ver_key.txt
set /p results_folder=<%LogFileDir%/results_folder.txt
set results_folder=%results_folder:/=\%
set results_file=%results_folder%\general.txt
If NOT EXIST "%results_folder%" md %results_folder%

Echo.
Echo copy %LogFileDir%\GeoDMSVersionInfo.txt to %results_file%
copy %LogFileDir%\GeoDMSVersionInfo.txt %results_file%
Echo.

Echo OS               : %OS% 
Echo StatusFlags      : %STATUSFLAGS%
Echo Computername     : %COMPUTERNAME%
Echo Startdate        : %Date% StartTime: %time% 
Echo Header           : %ver_key%

REM schrijf de relevanet versie informatie weg in de result file
Echo ^<statusflag^>%STATUSFLAGS%^</statusflag^> >> "%results_file%"
Echo ^<os^>%OS%^</os^> >> "%results_file%"
Echo ^<computername^>%COMPUTERNAME%^</B^>^<BR^> >> "%results_file%"
Echo ^<startdate^>%Date%^</startdate^>^<starttime^>%time%^</starttime^> >> "%results_file%"

