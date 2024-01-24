Rem voer 1 instantie van de operator test uit
Set RegrResult=OK
Set GeoDmsLogFilePath=%results_log_folder%\%6.txt
del %GeoDmsLogFilePath% 2>nul
Call full/SetStartTime.bat

Set command=%GeoDmsQtCmdBase% /L%GeoDmsLogFilePath% /T%1 %2 /%3 /%4 /%5  
Echo ****************
Echo.
Echo Test: %command%
%command%
Echo.
Echo ERRORLEVEL: %ERRORLEVEL%

Call full/SetEndTime.bat

Call full/WriteTimeStamps.bat %results_folder%\%6.txt

IF %ERRORLEVEL% NEQ 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %ERRORLEVEL%
)


