Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Set command=%GeoDmsRunCmdBase% /S1 /S2 /S3 %TstDir%\Unit\operator\cfg\select_orgrel.dms @statistics full/id 

Echo **************** Statistics 
Echo.
Echo Test: %command%
%command%

Echo.

rem pause

if %ERRORLEVEL% NEQ 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %ERRORLEVEL%
	Echo %GeoDmsRunCmdBase% /S1 /S2 /S3 %TstDir%\Unit\operator\cfg\select_orgrel.dms @statistics full/id  FAILED WITH ERRORLEVEL: %ERRORLEVEL% >> %ResultFileName%
)

Echo.
Echo end test
Echo ****************
Echo.


