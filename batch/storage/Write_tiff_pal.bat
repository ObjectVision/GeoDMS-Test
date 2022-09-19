Rem Storage Write Tiff palette based 

Set ResultFileTiff=%LocalDataDirRegression%\Storage\regr_results\tiff_pa.tif
Set ResultFilePal=%LocalDataDirRegression%\Storage\regr_results\tiff_pa.tfw

del %ResultFileTiff% 2>NUL
del %ResultFilePal% 2>NUL

echo GeoDMS Command: %GeoDmsRunCmdBase% "%StoragePath%" /Tiff/Palette/Write 
%GeoDmsRunCmdBase% "%StoragePath%" /Tiff/Palette/Write >> %LogFilePath%

echo.  >> %LogFilePath%

Rem vergelijk resultaten met referentie bestanden
echo File Compare: fc "%ResultFileTiff%" "%TstDir%\Storage\data\tiff_pa.tif" to %LogFilePath%
fc "%ResultFileTiff%" "%TstDir%\Storage\data\tiff_pa.tif" >> %LogFilePath% 

echo File Compare: fc "%ResultFilePal%" "%TstDir%\Storage\data\tiff_pa.tfw" to %LogFilePath%
fc "%ResultFilePal%" "%TstDir%\Storage\data\tiff_pa.tfw" >> %LogFilePath% 
echo.




