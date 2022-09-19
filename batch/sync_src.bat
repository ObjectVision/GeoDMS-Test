cls

call generic/SetRegressionTestSourceDataDir.bat
set AuthSourceRegrTests=\\OVSRV05\SourceData\RegressionTests
if /I "" EQU "%RegressionTestsSourceDataDir%" echo ERROR: environment variable RegressionTestsSourceDataDir not set. 
if ("%AuthSourceRegrTests%" EQU "%RegressionTestsSourceDataDir%") exit /B

CHOICE /M "Starten met SourceData RegressionTests robycopyen van "%AuthSourceRegrTests%" naar "%RegressionTestsSourceDataDir%" ? Runt dit op OVSRV05? Zeg dan Nee"
if ErrorLevel 2 goto end

robocopy "%AuthSourceRegrTests%" "%RegressionTestsSourceDataDir%" /E /purge /compress /np /nfl /ndl

pause "Klaar ?"
:end

