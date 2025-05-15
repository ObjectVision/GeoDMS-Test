REM Delete files made in previous runs, to be sured they are made againEcho.

Echo Removing files %LocalDataDirRegression%
set ERRORLEVEL=0
if "%SilentMode%" neq "QUIET" CHOICE /M "Wil je de folder (%LocalDataDirRegression%) met alle inhoud weggooien?"
if ErrorLevel 2 exit

rd /S /Q %LocalDataDirRegression% 
md %LocalDataDirRegression%
if ErrorLevel 1 exit



