Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Set command=%GeoDmsQtCmdBase% /T%1 /%4 /%5 /%6  "%2"
Echo ****************
Echo.
Echo Test: GeoDMS Command: %command%
%command%
Echo.

IF %ERRORLEVEL% EQU 0 (
	Echo read contents from file: %3
	Echo resultfilename: %ResultFileName%
	FOR /F "tokens=* delims=" %%x in (%3) DO Echo %%x

	FOR /F "tokens=* delims=" %%x in (%3) DO Echo %%x >> %ResultFileName%
	) Else (
	Echo TEST FAILED
	Echo ERRORLEVEL: %ERRORLEVEL%
	Echo GeoDMS Command: %command%  FAILED >> %ResultFileName%
)

Echo.
Echo end test
Echo ****************
Echo.

