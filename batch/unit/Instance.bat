Rem voer 1 instantie van de operator test uit
Rem
Rem Arguments: the configuration, the item to compute, the test log that item writes, and
Rem the three MT flags.
Rem
Rem A test passes when GeoDmsRun exits 0 AND leaves its test log empty. A configuration
Rem writes into that log only when it fails, in its own words: "... result: not OK" for
Rem nearly all of them, followed by the failing groups for the operator test. So a log
Rem with any text in it is a failing test, whatever it says, and gets a FAILED line in the
Rem aggregate followed by the log itself, the shape a nonzero exit and PythonTest.bat give.
Rem GeoDMS batch\run_unit_suite.bat, which is also the install gate of the setup scripts,
Rem grades the aggregate on FAILED. Until 2026-10-03 this script wrote only the log lines,
Rem and the D64 round of that morning, four operator groups failing, passed the gate.
Rem
Rem The log is deleted before the run, so the log graded is the one this run wrote. The
Rem export steps share their log with the test_log step after them, and the del lines at
Rem the top of unit_flagged.bat do not cover every result folder (unit\unit, grid, crs and
Rem Template have none; those for unit\operator and unit\storage deleted nothing until
Rem 2026-10-03, their closing quote stood after the stderr redirect), so an export step
Rem would otherwise grade the previous round's failure as its own.
Set RegrResult=OK

Set command=%GeoDmsRunCmdBase% /%4 /%5 /%6 %1 %2
Echo ****************
Echo.
Echo Test: GeoDMS Command: %command%
del "%~3" 2>nul
%command%
Set TestErrorLevel=%ERRORLEVEL%
Echo.

rem pause

IF %TestErrorLevel% NEQ 0 (
	Echo TEST FAILED
	Echo ERRORLEVEL: %TestErrorLevel%
	Echo %command% FAILED >> "%ResultFileName%"
	goto end
)

Echo read contents from file: %3
Echo resultfilename: "%ResultFileName%"
IF NOT EXIST "%~3" goto end
Set TestLogLines=0
FOR /F "usebackq tokens=* delims=" %%x in ("%~3") DO Set /A TestLogLines+=1
IF %TestLogLines% EQU 0 goto end

FOR /F "usebackq tokens=* delims=" %%x in ("%~3") DO Echo %%x
Echo TEST FAILED: the test log is not empty
Echo %command% FAILED, its test log reads: >> "%ResultFileName%"
FOR /F "usebackq tokens=* delims=" %%x in ("%~3") DO Echo %%x >> "%ResultFileName%"

:end
Echo.
Echo end test
Echo ****************
Echo.

