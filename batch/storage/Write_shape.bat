Rem Storage Write ESRI Shape Test

Set ResultFolder=%LocalDataDirRegression%\Storage\regr_results

del %ResultFolder%\point\point.* 2>NUL
del %ResultFolder%\arc\road.* 2>NUL
del %ResultFolder%\polygon\area.* 2>NUL

echo GeoDMS Command Point: %GeoDmsRunCmdBase% "%StoragePath%" /EsriShape/point/Write 
%GeoDmsRunCmdBase% "%StoragePath%" /EsriShape/point/Write >> %LogFilePath%

echo GeoDMS Command Arc: %GeoDmsRunCmdBase% "%StoragePath%" /EsriShape/arc/Write 
%GeoDmsRunCmdBase% "%StoragePath%" /EsriShape/arc/Write  >> %LogFilePath%

echo GeoDMS Command Polygon: %GeoDmsRunCmdBase% "%StoragePath%" /EsriShape/polygon/Write 
%GeoDmsRunCmdBase% "%StoragePath%" /EsriShape/polygon/Write   >> %LogFilePath%

echo.  >> %LogFilePath%

echo File Compare: fc "%ResultFolder%\point\point.*" "%TstDir%\Storage\data\point\point.*" to %LogFilePath%
fc "%ResultFolder%\point\point.*" "%TstDir%\Storage\data\point\point.*" >> %LogFilePath%

echo File Compare: fc "%ResultFolder%\arc\road.*" "%TstDir%\Storage\data\arc\road.*" to %LogFilePath%
fc "%ResultFolder%\arc\road.*" "%TstDir%\Storage\data\arc\road.*" >> %LogFilePath%

echo File Compare: fc "%ResultFolder%\polygon\area.*" "%TstDir%\Storage\data\polygon\area.*" to %LogFilePath%
fc "%ResultFolder%\polygon\area.*" "%TstDir%\Storage\data\polygon\area.*" >> %LogFilePath%

echo.

