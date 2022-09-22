Rem test gebaseerd op 7411, waar het updaten van een item en daarna afsluiten niet goed werkte (memory leaks, afsluiten bleef hangen)

Echo GeoDMS Command: %GeoDmsRunCmdBase% "%TstDir%\Operator\cfg\releasetest_7411_failure.dms" /direct/name TO %LogFilePath%
%GeoDmsRunCmdBase% "%TstDir%\Operator\cfg\releasetest_7411_failure.dms" /direct/name >> %LogFilePath%

Echo.

