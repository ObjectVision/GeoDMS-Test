REM Delete files made in previous runs, to be sured they are made againEcho.

Echo Removing files %LocalDataDirRegression%\*.dmsdata

del %tmpFileDir%\*.txt 2>nul
del %tmpFileDir%\*.html 2>nul
del %tmpFileDir%\*.log 2>nul
del %tmpFileDir%\dirinfo.str 2>nul

del %LocalDataDirRegression%\operator\dirinfo_pand_nhr.str 2>nul
del %LocalDataDirRegression%\BAG20\snapshot_Utrecht_20210701.gpkg 2>nul
del /S %LocalDataDirRegression%\*.dmsdata 2>nul