Rem voer 1 instantie van de operator test uit
Set RegrResult=OK

Echo ****************
Echo.
Echo Test: GeoDMS Command: %GeoDmsRunCmdBase% /%4 /%5 %1 %2 
%GeoDmsRunCmdBase% /%4 /%5 %1 %2
Echo.

rem pause

IF %ERRORLEVEL% EQU 0 (
	Echo read contents from file: %3
	Echo resultfilename: %ResultFileName%
	FOR /F "tokens=* delims=" %%x in (%3) DO Echo %%x
	
	FOR /F "tokens=* delims=" %%x in (%3) DO Echo %%x >> %ResultFileName%
	) Else (
	Echo TEST FAILED
	Echo %GeoDmsRunCmdBase% /%4 /%5 %1 %2 FAILED >> %ResultFileName%
)

Echo.
Echo end test
Echo ****************
Echo.

