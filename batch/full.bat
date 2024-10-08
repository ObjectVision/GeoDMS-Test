Rem Full test is de full test die een aantal GUI tests doet, operatoren op kleine en grote datasets test en die een aantal projecten test.
Rem version C1 C2 : PP1 && PP2 disabled, version S1 C2 : PP1 enabled && PP2 disabled, version S1 S2 : PP1 enabled && PP2 enabled

Echo off
CLS

set version=%1
set Setting1=%2
set Setting2=%3
set Setting3=%4

setlocal enabledelayedexpansion

Echo Starting the Full test
Echo.

Rem Sectie om LocalDataDir en SourceDataDir op te halen uit het Windows Registry en om de paden naar de lokale testprojecten en bijbehorende data te zetten
Call generic\SetLocalDataDir.bat
Call generic\SetSourceDataDir.bat

Rem Sectie om de folder te bepalen voor de logging en de status bestanden die uit de batch en door de GeoDMS worden weggeschreven.
Set LocalDataDirRegression=%LocalDataDir%\regression

Set tmpFileDir=%LocalDataDirRegression%\log
If NOT EXIST "%tmpFileDir%" md "%tmpFileDir%"

Call generic\SetGeoDMSPlatform.bat %version%
Call generic\SetRegressionTestSourceDataDir.bat 
Call generic\SetRelativePaths.bat

Set GeoDmsRunCmdBaseLarge="%GeoDmsRunPath%"
Set GeoDmsQtCmdBase="%GeoDmsGuiQtPath%" 

REM Call Full\DeletePreviousFiles.bat
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

REM Call Full\GUI_tests.bat
REM Call Full\Operator_tests.bat
Call Full\Project_tests.bat

REM Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t100_network_connect/result_html t100_network_connect


timeout /t 3

Call Full\MakeReport.bat




