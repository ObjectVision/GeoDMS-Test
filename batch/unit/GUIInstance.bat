Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Set command=%GeoDmsQtCmdBase% "/T%1" /%4 /%5 /%6 "%2"
Echo ****************
Echo.
Echo Test: GeoDMS Command: %command%
%command%
Echo.

IF %ERRORLEVEL% NEQ 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %ERRORLEVEL%
)

Echo.
Echo end test
Echo ****************
Echo.

