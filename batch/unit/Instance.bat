Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Set command=%GeoDmsRunCmdBase% /%4 /%5 /%6 %1 %2 
Echo ****************
Echo.
Echo Test: GeoDMS Command: %command%
%command%
Echo.

rem pause

IF %ERRORLEVEL% EQU 0 (
	Echo read contents from file: %3
	Echo resultfilename: "%ResultFileName%"
	FOR /F "tokens=* delims=" %%x in (%~3) DO Echo %%x

	FOR /F "tokens=* delims=" %%x in (%~3) DO Echo %%x >> "%ResultFileName%"
	) Else (
	Echo TEST FAILED
	Echo ERRORLEVEL: %ERRORLEVEL%
	Echo %command% FAILED >> "%ResultFileName%"
	pause
)

Echo.
Echo end test
Echo ****************
Echo.

