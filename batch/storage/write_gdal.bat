Rem GDAL StorageManager Write Test

Set ResultFolder=%LocalDataDirRegression%\Storage_gdal\regr_results

del %ResultFolder%\vect_write_regr.txt 2>NUL
del %ResultFolder%\grid_write_regr.txt 2>NUL

REM delete csv files
del %ResultFolder%\gdal_vect\csv\gdal_*.csv 2>NUL
del %ResultFolder%\gdal_vect\csv\gdal_*.csvt 2>NUL

REM delete dbf files
del %ResultFolder%\gdal_vect\dbf\gdal.dbf 2>NUL

REM delete shape files
del %ResultFolder%\gdal_vect\shp\arc.* 2>NUL
del %ResultFolder%\gdal_vect\shp\point.* 2>NUL
del %ResultFolder%\gdal_vect\shp\poly.* 2>NUL
del %ResultFolder%\gdal_vect\shp\poly_index.* 2>NUL
del %ResultFolder%\gdal_vect\shp\poly_mulev.* 2>NUL

REM delete gml files
del %ResultFolder%\gdal_vect\gml\waterdeel.gml 2>NUL
del %ResultFolder%\gdal_vect\gml\waterdeel.xsd 2>NUL

REM delete GeoJson files
del %ResultFolder%\gdal_vect\geoJSON\mask_ettenleur.geojson 2>NUL

REM delete GPKG files
del %ResultFolder%\gdal_vect\gpkg\multi_layer.gpkg 2>NUL
del %ResultFolder%\gdal_vect\gpkg\single_polygon_layer.gpkg 2>NUL

REM delete tiff files
del %ResultFolder%\gdal_grid\tiff\gdal_*.tif 2>NUL

REM genereer alle export files
echo GeoDMS Command, make all exports: %GeoDmsRunCmdBase% "%StorageGDALPath%" /export_all
%GeoDmsRunCmdBase% "%StorageGDALPath%" /export_all >> %LogFilePath%

REM gdal_vect
echo.
echo GeoDMS Command, VECT: %GeoDmsRunCmdBase% "%StorageGDALPath%" /results/vect_write_str
%GeoDmsRunCmdBase% "%StorageGDALPath%" /results/vect_write_str >> %LogFilePath%

echo. >> %LogFilePath%

echo File Compare: fc "%ResultFolder%\vect_write_regr.txt" "..\norm\true.txt" to %LogFilePath%
fc "%ResultFolder%\vect_write_regr.txt" "..\norm\true.txt" >> %LogFilePath% 

REM gdal_grid
echo.
echo GeoDMS Command, GRID: %GeoDmsRunCmdBase% "%StorageGDALPath%" /results/grid_write_str
%GeoDmsRunCmdBase% "%StorageGDALPath%" /results/grid_write_str >> %LogFilePath%

echo. >> %LogFilePath%

echo File Compare: fc "%ResultFolder%\grid_write_regr.txt" "..\norm\true.txt" to %LogFilePath%
fc "%ResultFolder%\grid_write_regr.txt" "..\norm\true.txt" >> %LogFilePath% 

echo.

