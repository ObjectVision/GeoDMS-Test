Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Echo ****************
Echo.
Echo Test: GeoDMS Command: %GeoDmsRunCmdBase% /%4 /%5 /%6 %1 %2
%GeoDmsRunCmdBase% /%4 /%5 /%6 %1 %2
Echo.

REM  pause

IF %ERRORLEVEL% EQU 0 (
	Echo TEST FAILED, ERROR EXPECTED
	Echo %GeoDmsRunCmdBase% /%4 /%5 %1 %2 FAILED, ERROR EXPECTED >> %ResultFileName%
	goto end
)

set ErrorIsAllowed=0
if %ERRORLEVEL% == 1 set ErrorIsAllowed=1
if %ERRORLEVEL% == 2 set ErrorIsAllowed=1

IF %ErrorIsAllowed% EQU 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %ERRORLEVEL%
	Echo %GeoDmsRunCmdBase% /%4 /%5 %1 %2 FAILED >> %ResultFileName%
)

:end
Echo.
Echo end test
Echo ****************
Echo.
