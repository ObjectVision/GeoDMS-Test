Rem Run one geodms python-bindings test script against the build under test.
Rem   %1 = full path to the python test script (it must print PASS/FAIL and exit 0/1)
Rem   %2 = full path to the per-test output file
Rem
Rem The geodms module (geodms.pyd) lives in the build's bin dir (same folder as
Rem GeoDmsRun.exe), which SetGeoDMSPlatform.bat exposed as %GeoDmsPath%. The .pyd is
Rem built for a specific CPython version (currently 3.13), so by default we select that
Rem interpreter via the 'py' launcher; override with the PYTHON_EXE environment variable.

Set GEODMS_PYDIR=%GeoDmsPath%

IF "%PYTHON_EXE%"=="" ( Set PyCmd=py -3.13 ) ELSE ( Set PyCmd="%PYTHON_EXE%" )

Echo ****************
Echo.
Echo Test: %PyCmd% %1
Echo   GEODMS_PYDIR=%GEODMS_PYDIR%
Echo.

%PyCmd% -u "%~1" > "%~2" 2>&1 < nul

IF %ERRORLEVEL% EQU 0 (
	Echo  --- PASS ---
	FOR /F "usebackq tokens=* delims=" %%x in ("%~2") DO Echo %%x
	Echo python %~nx1 OK >> "%ResultFileName%"
) ELSE (
	Echo  --- FAILED ^(exit %ERRORLEVEL%^) ---
	FOR /F "usebackq tokens=* delims=" %%x in ("%~2") DO Echo %%x
	Echo python %~nx1 FAILED >> "%ResultFileName%"
	FOR /F "usebackq tokens=* delims=" %%x in ("%~2") DO Echo %%x >> "%ResultFileName%"
)

Echo.
Echo end test
Echo ****************
Echo.
