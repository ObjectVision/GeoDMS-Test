Rem Storage Write dbf Test

Set ResultFile=%LocalDataDirRegression%\Storage\regr_results\dbf.dbf

del %ResultFile% 2>NUL

echo GeoDMS Command: %GeoDmsRunCmdBase% "%StoragePath%" /dbf/Write
%GeoDmsRunCmdBase% "%StoragePath%" /dbf/Write >> %LogFilePath%

echo.  >> %LogFilePath%

Rem vergelijk resultaten met referentie bestanden
echo File Compare: fc "%ResultFile%" "%TstDir%\Storage\data\dbf.dbf" to %LogFilePath%
fc "%ResultFile%" "%TstDir%\Storage\data\dbf.dbf" >> %LogFilePath% 

echo.
