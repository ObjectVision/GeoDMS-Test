Rem Call a Specific Test

if %RegrResult%==FAILED goto End

if "%LogFilePath%" EQU "" (Echo "environment variable LogFilePath must be set" && pause)
if exist %LogFilePath% del %LogFilePath%

Echo ****************
Echo start test: %1 in the folder:  %BatchDir%
Echo.

Call %1
	if not errorlevel 1 (Echo Result: OK ) Else (
		Set RegrResult=FAILED
		Echo !!! %BatchFile% FAILED
		Echo !!! %BatchFile% FAILED >> %LogFilePath%
		type %LogFilePath% >> %LogFilePath%
	)

Echo.
Echo end test
Echo ****************
Echo.

: End