Echo off
CLS

Rem Test is de FAST regressietest die een aantal GUI tests doet en de operatoren en storages test
Rem naast deze FAST test is er ook een FULL test die projecten en meer tijdrovende modeldelen test

set version=%1
if (%2)==() ( Echo off ) else ( Echo %2 )
if (%1)==() ( Echo Usage: TEST.BAT ^[D32^|R32^|D64^|R64^|^<versionNr^>]
			  GoTo End)

setlocal enabledelayedexpansion

Set RegrResult=OK

Rem Sectie om LocalDataDir en SourceDataDir op te halen uit het Windows Registry en om de paden naar de lokale testprojecten en bijbehorende data te zetten
Call generic\SetLocalDataDir.bat
Call generic\SetSourceDataDir.bat

Rem Sectie om de folder te bepalen voor de logging en de status bestanden die uit de batch en door de GeoDMS worden weggeschreven.
Set LocalDataDirRegression=%LocalDataDir%\regression
Set LogFileDir=%LocalDataDirRegression%\log
If NOT EXIST "%LogFileDir%" md "%LogFileDir%"
Set LogFilePath=%LogFileDir%\GeoDmsTemp.txt

Call generic\SetGeoDMSPlatform.bat %version%
Call generic\SetRegressionTestSourceDataDir.bat
Call generic\SetRelativePaths.bat

Set GeoDmsRunCmdBase="%GeoDmsRunPath%" /L"%LogFilePath%" 
Set GeoDmsRunCmdBaseLarge=%GeoDmsRunCmdBase%

Echo.
Echo ************************
Echo Starting the Fast test for: %GeoDmsRunPath%
Echo ************************
Echo.

Echo Used Folders

Echo ************************
Echo LocalDataDirRegression  : %LocalDataDirRegression%
Echo TstDir                  : %TstDir%
Echo ************************
Echo.

Echo.
Echo ************************
Echo Removing files %LocalDataDirRegression%\*.dmsdata
del /S %LocalDataDirRegression%\*.dmsdata 2>NUL
Echo.

Echo.
Echo START TESTING
Echo.

REM SECTIE GUI TESTS
SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\gui
Call Gui\MapViewClassification.bat 
Call Gui\RSLight_2020_Expand.bat 

REM SECTIE OPERATOR TESTS
SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\operator
Call Fast\InstanceOperator.bat C1 C2 %OperatorPath% results/tests_log operator_test_C1C2
Call Fast\InstanceOperator.bat S1 C2 %OperatorPath% results/tests_log operator_test_S1C2
Call Fast\InstanceOperator.bat S1 S2 %OperatorPath% results/tests_log operator_test_S1S2
Call Fast\InstanceOperator.bat C1 S2 %OperatorPath% results/tests_log operator_test_C1S2

REM SECTIE OVERIGE FAST TESTS
Call Fast\instance.bat fast/Mini.bat
Call Fast\instance.bat fast/releasetest_7411_failure.bat


REM SECTIE GEODMS STORAGEMANAGER TESTS
SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\storage
Call Fast\instance.bat Storage/Read.bat

Call Fast\instance.bat Storage/Write_dbf.bat
Call Fast\instance.bat Storage/Write_str.bat
Call Fast\instance.bat Storage/Write_ASCII_grid_uc.bat
Call Fast\instance.bat Storage/Write_tiff_pal.bat
Call Fast\instance.bat Storage/Write_Shape
Call Fast\instance.bat Storage/Write_fss.bat

REM SECTIE GDAL STORAGEMANAGER TESTS
SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\storage_gdal
Call Fast\instance.bat Storage/Read_gdal_vect.bat
Call Fast\instance.bat Storage/Read_gdal_grid.bat
Call Fast\instance.bat Storage/write_gdal.bat

Echo.
Echo ************************
Echo.
Echo Fast Test: %RegrResult%
Echo.
Echo ************************

Echo End Logging >> %LogFilePath%

Set Sequence=%date:/=-%_%time::=-%
SET LogFileFinalName=v%1_%RegrResult%_%Sequence%.txt
RENAME "%LogFilePath%" "%LogFileFinalName%"
Echo Log Information written to "%LogFileDir%\%LogFileFinalName%"
Echo.

IF not %RegrResult% == OK (
	"%ProgramFiles%\Notepad++\Notepad++.exe"  "%LogFileDir%\%LogFileFinalName%"
)

: End