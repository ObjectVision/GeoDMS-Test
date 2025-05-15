Rem Full test is de full test die een aantal GUI tests doet, operatoren op kleine en grote datasets test en die een aantal projecten test.
Rem version C1 C2 : PP1 && PP2 disabled, version S1 C2 : PP1 enabled && PP2 disabled, version S1 S2 : PP1 enabled && PP2 enabled

Echo off
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

Call Full\DeletePreviousFiles.bat
Set tmpFileDir=%LocalDataDirRegression%\log
If NOT EXIST "%tmpFileDir%" md "%tmpFileDir%"
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

pause

CLS

Echo START TESTING

Call Full\GUI_tests.bat
Call Full\Operator_tests.bat
Call Full\Project_tests.bat

REM Call Full\Project_tests_enkelProject.bat
REM Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t100_network_connect/result_html t100_network_connect


timeout /t 3

Call Full\MakeReport.bat




