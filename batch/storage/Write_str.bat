Rem Storage Write strfiles Test

Set ResultFolder=%LocalDataDirRegression%\Storage\regr_results\strfiles\regr

del %ResultFolder%\*.txt 2>NUL

echo GeoDMS Command strParam: %GeoDmsRunCmdBase% "%StoragePath%" /str/Write/StringParam 
%GeoDmsRunCmdBase% "%StoragePath%" /str/Write/StringParam >> %LogFilePath%

echo GeoDMS Command strUInt8Array: %GeoDmsRunCmdBase% "%StoragePath%" /str/Write/UInt8Array
%GeoDmsRunCmdBase% "%StoragePath%" /str/Write/UInt8Array >> %LogFilePath%

echo GeoDMS Command strFiles %GeoDmsRunCmdBase% "%StoragePath%" /strfiles/Write
%GeoDmsRunCmdBase% "%StoragePath%" /strfiles/Write >> %LogFilePath%

echo.  >> %LogFilePath%
echo.

Rem vergelijk resultaten met referentie bestanden
echo File Compare: fc "%ResultFolder%\*.txt" "%TstDir%\Storage\data\strfiles\regr\*.txt" to %LogFilePath%
fc "%ResultFolder%\*.txt" "%TstDir%\Storage\data\strfiles\regr\*.txt" >> %LogFilePath%

echo.


