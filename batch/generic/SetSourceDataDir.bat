Rem Lees de SourceDataDir uit de registry en zet de waarde als environment variable

if not ("%SourceDataDir%")==("") goto skipSourceDataDir
:: delims is a TAB followed by a space
FOR /F "tokens=2* delims=	 " %%A IN ('REG QUERY "HKCU\Software\ObjectVision\%COMPUTERNAME%\GeoDMS" /v SourceDataDir') DO SET SourceDataDir=%%B
if not ("%SourceDataDir%")==("") goto skipSourceDataDir
FOR /F "tokens=2* delims=	 " %%A IN ('REG QUERY "HKCU\Software\ObjectVision\DMS" /v SourceDataDir') DO SET SourceDataDir=%%B
: skipSourceDataDir

If NOT EXIST "%SourceDataDir%" md "%SourceDataDir%"
