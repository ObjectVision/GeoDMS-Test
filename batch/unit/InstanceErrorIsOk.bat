Rem voer 1 instantie van de operator test uit, deze slaagt als er een error wordt opgegooid (verwacht gedrag)
Set RegrResult=OK

Set command=%GeoDmsRunCmdBase% /%4 /%5 /%6 %1 %2
Echo ****************
Echo.
Echo Test: GeoDMS Command: %command%
%command%
REM Capture the exit code BEFORE anything else: a successful SET resets ERRORLEVEL to 0, so
REM reading %ERRORLEVEL% after "set ErrorIsAllowed=0" always yielded 0 and no exit code could
REM ever be accepted -- every test wrapped by this script reported FAILED regardless.
Set TestErrorLevel=%ERRORLEVEL%
Echo.

REM  pause

IF %TestErrorLevel% EQU 0 (
	Echo TEST FAILED, ERROR EXPECTED
	Echo %GeoDmsRunCmdBase% /%4 /%5 %1 %2 FAILED, ERROR EXPECTED >> %ResultFileName%
	goto end
)

set ErrorIsAllowed=0
if %TestErrorLevel% == 1 set ErrorIsAllowed=1
if %TestErrorLevel% == 2 set ErrorIsAllowed=1

IF %ErrorIsAllowed% EQU 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %TestErrorLevel%
	Echo %GeoDmsRunCmdBase% /%4 /%5 %1 %2 FAILED >> %ResultFileName%
)

:end
Echo.
Echo end test
Echo ****************
Echo.
