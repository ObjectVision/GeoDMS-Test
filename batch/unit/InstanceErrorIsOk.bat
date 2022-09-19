Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Echo ****************
Echo.
Echo Test: GeoDMS Command: %GeoDmsRunCmdBase% /%4 /%5 %1 %2 
%GeoDmsRunCmdBase% /%4 /%5 %1 %2
Echo.

REM  pause

IF %ERRORLEVEL% EQU 0 (
	Echo TEST FAILED, ERROR EXPECTED
	Echo %GeoDmsRunCmdBase% /%4 /%5 %1 %2 FAILED, ERROR EXPECTED >> %ResultFileName%
)

Echo.
Echo end test
Echo ****************
Echo.
