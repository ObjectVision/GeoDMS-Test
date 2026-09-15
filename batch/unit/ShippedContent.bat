Rem The .dms content the installer ships, run from the build under test (GeoDMS-Test #24):
Rem <GeoDmsPath>\examples\testcases\run_testcases.bat against that build's GeoDmsRun, the way a
Rem user runs it from <install>\examples\testcases. Its shipped_*.dms cases include every
Rem library\ file and both examples from %exeDir%, so a shipped configuration that no longer
Rem loads or computes fails here, from the installed copy.
Rem
Rem When the unit suite gates a setup (BuildSignAndCreateSetup{,Cmake}.bat run unit.bat right
Rem after the silent install), this is what makes such a break take the install down with it.
Rem A build without a shipped battery (before 20.16.0) records a skip line, not a failure, so
Rem the suite still runs against older versions. A build that has it and fails it writes a
Rem FAILED line, which run_unit_suite.bat gates on.
Rem
Rem %GeoDmsPath%, %GeoDmsRunPath% and %ResultFileName% come from unit_flagged.bat. The MT flags
Rem are not passed on: the battery runner sets none, as it does for a user.

Echo ****************
Echo.
Echo Test: shipped content of %GeoDmsPath%
Echo.

Set ShippedBattery=%GeoDmsPath%\examples\testcases\run_testcases.bat
IF EXIST "%ShippedBattery%" (
	Call "%ShippedBattery%" "%GeoDmsRunPath%"
	IF ERRORLEVEL 1 (
		Echo  --- shipped testcases battery FAILED ---
		Echo shipped examples\testcases battery FAILED >> "%ResultFileName%"
	) ELSE (
		Echo  --- shipped testcases battery PASS ---
		Echo shipped examples\testcases battery OK >> "%ResultFileName%"
	)
) ELSE (
	Echo  --- no shipped examples\testcases in this build, skipped ---
	Echo shipped examples\testcases battery not shipped by this build, skipped >> "%ResultFileName%"
)

Echo.
Echo end test
Echo ****************
Echo.
