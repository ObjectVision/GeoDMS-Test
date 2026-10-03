Rem voer 1 instantie van een GUI test uit
Rem
Rem Arguments: the dmsscript, the configuration, a file that no dmsscript writes (gui_instance.sh
Rem appends it to the aggregate when it exists; this script ignores it), and the three MT flags.
Rem
Rem A nonzero exit of GeoDmsGuiQt, such as the exit 3 of a Debug dms_assert, gets a FAILED line
Rem in the aggregate, as gui_instance.sh writes one; GeoDMS batch\run_unit_suite.bat grades the
Rem aggregate on it. Until 2026-10-03 this script only echoed TEST FAILED to the console, so a
Rem GUI test that crashed passed the gate.
Set RegrResult=OK

Set command=%GeoDmsQtCmdBase% "/T%~1" /%4 /%5 /%6 "%~2"
Echo ****************
Echo.
Echo Test: GeoDMS Command: %command%
%command%
Set TestErrorLevel=%ERRORLEVEL%
Echo.

IF %TestErrorLevel% NEQ 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %TestErrorLevel%
	Echo %command% FAILED WITH ERRORLEVEL: %TestErrorLevel% >> "%ResultFileName%"
)

Echo.
Echo end test
Echo ****************
Echo.

