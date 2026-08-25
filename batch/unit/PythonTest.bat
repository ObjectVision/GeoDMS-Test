Rem Run one geodms python-bindings test script against the build under test.
Rem   %1 = full path to the python test script (it must print PASS/FAIL and exit 0/1)
Rem   %2 = full path to the per-test output file
Rem
Rem The geodms extension lives in the build's bin dir (same folder as GeoDmsRun.exe),
Rem which SetGeoDMSPlatform.bat exposed as %GeoDmsPath%. It is an ABI-TAGGED CPython
Rem extension (geodms.cp<XY>-win_amd64.pyd), and WHICH CPython it is built for is
Rem FLAVOUR-SPECIFIC -- the GeoDMS repo pins that per flavour:
Rem   m / c / l : python\PythonVersions.txt       -> 3.12;3.13;3.14, any of which the
Rem               'py' launcher can provide; the build ships one extension per version.
Rem   g         : python\PythonVersionsGlobio.txt -> 3.9, and it has to be the CPython OF
Rem               THE LOCKED GLOBIO CONDA PREFIX (%GLOBIO_ENV_ROOT%\python.exe). NOT
Rem               'py -3.9': that resolves to whatever stock 3.9 is registered, which
Rem               supplies a python39.dll but not the GDAL 3.1.4 the extension binds.
Rem Running an interpreter the extension was not built for reports
Rem "ModuleNotFoundError: No module named 'geodms'" -- the extension IS there, it just
Rem does not match that interpreter's ABI tag.
Rem
Rem So: the flavour (%GeoDmsFlavor%, exported by unit_flagged.bat) decides WHERE the
Rem interpreter comes from, and for m/c/l the extensions the build actually shipped
Rem decide WHICH version -- the first tag whose 'py -X.Y' resolves on this machine.
Rem PYTHON_EXE overrides everything.

Set GEODMS_PYDIR=%GeoDmsPath%
Set PyCmd=

IF NOT "%PYTHON_EXE%"=="" (
	Set PyCmd="%PYTHON_EXE%"
	goto :have_interpreter
)

IF /I "%GeoDmsFlavor%"=="g" (
	IF "%GLOBIO_ENV_ROOT%"=="" (
		Echo *** GLOBIO_ENV_ROOT is not set: cannot select the g-flavour CPython ***
		Echo python %~nx1 FAILED ^(GLOBIO_ENV_ROOT not set^) >> "%ResultFileName%"
		goto :eof
	)
	Set PyCmd="%GLOBIO_ENV_ROOT%\python.exe"
	goto :have_interpreter
)

for /f "delims=" %%P in ('dir /b "%GeoDmsPath%\geodms.cp*-win_amd64.pyd" 2^>nul') do call :try_pyd "%%P"
Rem No tagged extension (a build from before the multi-version bindings), or none of the
Rem shipped versions is installed here: fall back to the long-standing default.
IF "%PyCmd%"=="" Set PyCmd=py -3.13
goto :have_interpreter

:try_pyd
IF NOT "%PyCmd%"=="" goto :eof
Set _pyd=%~1
Set _pyd=%_pyd:geodms.cp=%
Set _pyd=%_pyd:-win_amd64.pyd=%
Set _ver=%_pyd:~0,1%.%_pyd:~1%
py -%_ver% -c "pass" >nul 2>&1
IF ERRORLEVEL 1 (
	Echo   skipping shipped %~1: no CPython %_ver% on this machine
	goto :eof
)
Set PyCmd=py -%_ver%
goto :eof

:have_interpreter
Echo ****************
Echo.
Echo Test: %PyCmd% %1
Echo   GEODMS_PYDIR=%GEODMS_PYDIR%
Echo   flavour=%GeoDmsFlavor%
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
