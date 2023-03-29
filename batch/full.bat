Rem Full test is de full test die een aantal GUI tests doet, operatoren op kleine en grote datasets test en die een aantal projecten test.
Rem version C1 C2 : PP1 && PP2 disabled, version S1 C2 : PP1 enabled && PP2 disabled, version S1 S2 : PP1 enabled && PP2 enabled

Echo off
CLS

set version=%1
set Setting1=%2
set Setting2=%3

setlocal enabledelayedexpansion

Echo Starting the Full test
Echo.

Rem Sectie om LocalDataDir en SourceDataDir op te halen uit het Windows Registry en om de paden naar de lokale testprojecten en bijbehorende data te zetten
Call generic\SetLocalDataDir.bat
Call generic\SetSourceDataDir.bat

Rem Sectie om de folder te bepalen voor de logging en de status bestanden die uit de batch en door de GeoDMS worden weggeschreven.
Set LocalDataDirRegression=%LocalDataDir%\regression
Set LogFileDir=%LocalDataDirRegression%\log
If NOT EXIST "%LogFileDir%" md "%LogFileDir%"
Set GeoDmsLogFilePath=%LogFileDir%\GeoDmsTemp.txt

Call generic\SetGeoDMSPlatform.bat %version%
Call generic\SetRegressionTestSourceDataDir.bat 
Call generic\SetRelativePaths.bat

Set GeoDmsRunCmdBaseLarge="%GeoDmsRunPath%" /L"%GeoDmsLogFilePath%" 

Call Full\DeletePreviousFiles.bat
Call Full\EchoFolders.bat

Echo GeoDMS Version information
Echo ************************

Call Full\Header.bat %Setting1% %Setting2%
Set /p results_folder=<%LogFileDir%/results_folder.txt
Set results_folder=%results_folder:/=\%

Echo resultaat folder : %results_folder%
Echo.

pause

CLS

Echo START TESTING

Call Full\GUI_tests.bat
Call Full\Operator_tests.bat
Call Full\Project_tests.bat

REM Full\Project_tests_alleenRS.bat
REM Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t300_xml_ReadParse/result_html t300_xml_ReadParse
REM Call Full\InstanceTimeStampStatistics.bat %Setting1% %Setting2% %OperatorPath% /Arithmetics/UnTiled/add/attr t1742_command_statistics "%TstDir%\norm\Statistics_AUAA.txt"


Call Full\MakeReport.bat

