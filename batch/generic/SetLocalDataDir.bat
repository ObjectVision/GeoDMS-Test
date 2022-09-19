Rem Lees de LocalDataDir uit de registry en zet de waarde als environment variable

if not (%LocalDataDir%)==() goto skipLocalDataDir
:: delims is a TAB followed by a space
FOR /F "tokens=2* delims=	 " %%A IN ('REG QUERY "HKCU\Software\ObjectVision\%COMPUTERNAME%\GeoDMS" /v LocalDataDir') DO SET LocalDataDir=%%B
if not (%LocalDataDir%)==() goto skipLocalDataDir
FOR /F "tokens=2* delims=	 " %%A IN ('REG QUERY "HKCU\Software\ObjectVision\DMS" /v LocalDataDir') DO SET LocalDataDir=%%B
: skipLocalDataDir

If NOT EXIST "%LocalDataDir%" md "%LocalDataDir%"
