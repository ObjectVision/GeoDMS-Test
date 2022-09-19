Rem Storage Write ASCII grid with configured unit Test

Set ResultFile=%LocalDataDirRegression%\Storage\regr_results\ASCII_grid_uc.asc

del %ResultFile% 2>NUL

echo GeoDMS Command: %GeoDmsRunCmdBase% "%StoragePath%" /ASCIIgrid/Write/GridData
%GeoDmsRunCmdBase% "%StoragePath%" /ASCIIgrid/Write/GridData >> %LogFilePath%

echo.  >> %LogFilePath%

Rem vergelijk resultaten met referentie bestanden
echo File Compare: fc "%ResultFile%" "%TstDir%\Storage\data\testgrid.asc" to %LogFilePath%
fc "%ResultFile%" "%TstDir%\Storage\data\testgrid.asc" >> %LogFilePath%

echo.


