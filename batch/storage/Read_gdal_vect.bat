Rem GDAL StorageManager VECT Read Test

Set ResultFile=%LocalDataDirRegression%\Storage_gdal\regr_results\vect_read_regr.txt
del %ResultFile% 2>NUL

echo GeoDMS Command: %GeoDmsRunCmdBase% "%StorageGDALPath%" /results/vect_read_str 
%GeoDmsRunCmdBase% "%StorageGDALPath%" /results/vect_read_str  >> %LogFilePath%

echo.

Rem vergelijk resultaten met wat referentie waarde
echo File Compare: fc %ResultFile% "%TstDir%\norm\true.txt" to %LogFilePath%
fc "%ResultFile%" "%TstDir%\norm\true.txt" >> "%LogFilePath%"
echo.