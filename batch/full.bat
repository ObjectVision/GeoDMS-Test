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

Call Full\DeletePreviousFiles.bat
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

CLS

Echo START TESTING

Call Full\GUI_tests.bat
REM Call Full\Operator_tests.bat
REM Call Full\Project_tests.bat

REM Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %DynaPopPath% t810_ValLuisa_Czech_LU_POP/result t810_ValLuisa_Czech_LU_POP 
REM Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %DynaPopPath% Runs/Czechia/CaseData/JrcFactorData/TiffData/Erodibility  t810_ValLuisa_Czech_LU_POP 

REM SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\Vesta
REM Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %VestaRunPath% t510_indicator_results_test/result_html t510_vesta_indicator_results_test


REM Call Full\InstanceTimeStampStatistics.bat %Setting1% %Setting2% %Setting3% %OperatorPath% /Arithmetics/UnTiled/add/attr t1742_command_statistics "%TstDir%\norm\Statistics_AUAA.html"

timeout /t 3
REM Call Full\RSOpen.bat %Setting1% %Setting2% %Setting3% t640_RSopen

Call Full\MakeReport.bat




