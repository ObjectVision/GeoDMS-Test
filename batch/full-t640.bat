Rem Full test is de full test die een aantal GUI tests doet, operatoren op kleine en grote datasets test en die een aantal projecten test.
Rem version C1 C2 : PP1 && PP2 disabled, version S1 C2 : PP1 enabled && PP2 disabled, version S1 S2 : PP1 enabled && PP2 enabled

Echo on
CLS

set version=%1
set Setting1=%2
set Setting2=%3
set Setting3=%4
set SilentMode=%5

setlocal enabledelayedexpansion

Echo Starting the Full test
Echo.

Call generic\SetGeoDMSPlatform.bat %version%
Call generic\SetRelativePaths.bat

Rem Sectie om de folder te bepalen voor de logging en de status bestanden die uit de batch en door de GeoDMS worden weggeschreven.
Set LocalDataDirRegression=%LocalDataDir%\regression

Set GeoDmsRunCmdBaseLarge="%GeoDmsRunPath%"
Set GeoDmsQtCmdBase="%GeoDmsGuiQtPath%" 

REM Call Full\DeletePreviousFiles.bat
Set tmpFileDir=%LocalDataDirRegression%\log
If NOT EXIST "%tmpFileDir%" md "%tmpFileDir%"
echo off
Call Full\EchoFolders.bat


Echo GeoDMS Version information
Echo ************************

Call Full\Header.bat %Setting1% %Setting2% %Setting3%
Set /p results_folder=<%tmpFileDir%/results_folder.txt
Set results_folder=%results_folder:/=\%
Set results_log_folder=%results_folder%\log
If NOT EXIST "%results_log_folder%" md "%results_log_folder%"

Echo resultaat folder : %results_folder%
Echo resultaat log folder : %results_log_folder%
Echo.

if "%SilentMode%" neq "QUIET" pause

CLS

Echo START TESTING

REM Testen van projecten

REM SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\RS
REM Call Full\RSOpen.bat %Setting1% %Setting2% %Setting3% t640_3_RSopen_indicator_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\RS_v2025
Call Full\RSOpen_v2025.bat %Setting1% %Setting2% %Setting3% t641_3_RSopen_indicator_results_test

timeout /t 3

Call Full\MakeReport.bat




