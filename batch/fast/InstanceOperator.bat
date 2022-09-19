Rem voer 1 instantie van de operator test uit

if %RegrResult%==FAILED goto End

if "%LogFilePath%" EQU "" (Echo "environment variable LogFilePath must be set" && pause)
if exist %LogFilePath% del %LogFilePath%

Set ResultFile=%LocalDataDirRegression%\operator\regr_results\operator.txt
if exist %ResultFile% del %ResultFile%

Set BatchFile=%TstDir%\Operator\cfg\operator.dms

echo ****************
echo start test: %BatchFile%, %5
echo.
echo Test: GeoDMS Command: %GeoDmsRunCmdBase% /%1 /%2 %3 %4 
%GeoDmsRunCmdBase% /%1 /%2 %3 %4 > %LogFilePath%
echo.

Rem vergelijk resultaten met wat referentie waarde
echo File Compare: fc %ResultFile% "%TstDir%\norm\true.txt" to %LogFilePath%
fc %ResultFile% "%TstDir%\norm\true.txt" >> %LogFilePath%
echo.


if not errorlevel 1 (echo Result: OK ) Else (
	Set RegrResult=FAILED
	echo Result: !!! %BatchFile%, %5 FAILED
	echo Result: !!! %BatchFile%, %5 FAILED >> %LogFilePath%
)

Echo.
Echo end test
Echo ****************
Echo.

: End

