Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Echo **************** Statistics 
Echo.

Echo Test: %GeoDmsRunCmdBase% /S1 /S2 %TstDir%\Unit\operator\cfg\select_orgrel.dms @statistics full/id 

%GeoDmsRunCmdBase% /S1 /S2 %TstDir%\Unit\operator\cfg\select_orgrel.dms @statistics full/id 

Echo.

rem pause

if %ERRORLEVEL% NEQ 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %ERRORLEVEL%
	Echo %GeoDmsRunCmdBase% /S1 /S2 %TstDir%\Unit\operator\cfg\select_orgrel.dms @statistics full/id  FAILED WITH ERRORLEVEL: %ERRORLEVEL% >> %ResultFileName%
)

Echo.
Echo end test
Echo ****************
Echo.


