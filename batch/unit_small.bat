Echo off
CLS

set version=%1
if (%2)==() ( Echo off ) else ( Echo %2 )
if (%1)==() ( Echo Usage: UNIT.BAT ^[D32^|R32^|D64^|R64^|^<versionNr^>]
			  GoTo End)

REM SECTION SET RELEVANT DIRS
Call generic\SetLocalDataDir.bat
Set ResultDir=%LocalDataDir%\GeoDMSTestResults
Set ResultFileName=%ResultDir%\unit\result.txt
Call generic\SetGeoDMSPlatform.bat %version%

Set GeoDmsRunCmdBase="%GeoDmsRunPath%" 
Set GeoDmsQtCmdBase="%GeoDmsGuiQtPath%" 

set BatchDir=%CD%
cd ..
set TstDir=%CD%
cd %BatchDir%

REM SECTION LOGGING
Echo.
Echo ************************
Echo Starting the UNIT test for: %GeoDmsRunCmdBase%
Echo ************************
Echo.
Echo TstDir: %TstDir%
Echo ResultDir: %ResultDir%
Echo.

REM REMOVE OLD RESULTS
del %ResultDir%\unit\operator\*.txt 2>nul
del %ResultDir%\unit\storage\*.txt 2>nul
del %ResultDir%\unit\storage\*.dbf 2>nul
del %ResultDir%\unit\storage\*.tif 2>nul
del %ResultDir%\unit\storage\*.tfw 2>nul
del %ResultDir%\unit\storage\OneRecord.fss\*.dmsdata 2>nul
del %ResultDir%\unit\storage\OneRecord.fss\*.fss 2>nul
del %ResultDir%\unit\storage\ZeroRecord.fss\*.dmsdata 2>nul
del %ResultDir%\unit\storage\ZeroRecord.fss\*.fss 2>nul
del %ResultDir%\unit\GUI\*.txt 2>nul

rem pause

del %ResultDir%\unit\integrity_check\*.txt 2>nul
del %ResultDir%\unit\Namespaces\*.txt 2>nul
del %ResultDir%\unit\other\*.txt 2>nul

del %ResultFileName% 2>nul


rem pause

Echo Unit Test Results (specific operators, all operators, storage read, other) for: %GeoDmsRunCmdBase% >> %ResultFileName%
Echo.>> %ResultFileName%


REM SECTION GUI 
REM Call Unit\GUIInstance.bat %TstDir%\dmsscript\MapViewClassification.dmsscript %TstDir%\Operator\cfg\MicroTst.dms %ResultDir%\unit\gui\MicroTst_error.txt S1 S2 S3

REM Call ..\Unit\GUI\bat\DPGeneral_explicit_supplier_error.bat
REM Call Unit\Instance.bat %TstDir%\Unit\GUI\cfg\DPGeneral_explicit_supplier_error.dms test_log %ResultDir%\unit\gui\DPGeneral_ES_error.txt S1 S2 S3

Call ..\Unit\GUI\bat\DPGeneral_explicit_supplier_error_qt.bat
REM Call Unit\Instance.bat %TstDir%\Unit\GUI\cfg\DPGeneral_explicit_supplier_error.dms test_log %ResultDir%\unit\gui\DPGeneral_ES_error.txt S1 S2 S3



IF %ERRORLEVEL% NEQ 0 Echo "%GeoDmsGuiQtPath%" FAILED >> %ResultFileName%


REM SECTION MAKE FINAL RESULT FILE AND PRESENT IN NOTEPAD ++
Set Sequence=%date:/=-%_%time::=-%
SET ResultFileFinalName=v%1_%Sequence%.txt
RENAME "%ResultFileName%" "%ResultFileFinalName%"

CALL "%ProgramFiles%\Notepad++\Notepad++.exe"  "%ResultDir%\unit\%ResultFileFinalName%"
