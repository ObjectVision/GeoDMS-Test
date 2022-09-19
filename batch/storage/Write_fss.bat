Rem Storage Write fss Test

Set ResultFolder=%LocalDataDirRegression%\Storage\regr_results\fss_test

del %ResultFolder%\att*.dmsdata 2>NUL

echo GeoDMS Command: %GeoDmsRunCmdBase% "%StoragePath%" /fss/Make
%GeoDmsRunCmdBase% "%StoragePath%" /fss/Make >> %LogFilePath%

echo.  >> %LogFilePath%

Rem vergelijk resultaten met referentie bestanden
echo File Compare: fc "%ResultFolder%\att*.dmsdata" "%TstDir%\Storage\data\fss_test\att*.dmsdata" to %LogFilePath%
fc "%ResultFolder%\att*.dmsdata" "%TstDir%\Storage\data\fss_test\att*.dmsdata" >> %LogFilePath% 

echo.

