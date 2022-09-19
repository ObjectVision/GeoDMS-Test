Rem GeoDMS StorageManager Read Test

Set ResultFile=%LocalDataDirRegression%\Storage\regr_results\read_regr.txt

del %ResultFile% 2>NUL

Echo GeoDMS Command: %GeoDmsRunCmdBase% "%StoragePath%" /results/read_str
%GeoDmsRunCmdBase% "%StoragePath%" /results/read_str >> %LogFilePath%

Echo.

Rem vergelijk resultaten met wat referentie waarde
Echo File Compare: fc %ResultFile% "%TstDir%\norm\true.txt" to %LogFilePath%
fc "%ResultFile%" "%TstDir%\norm\true.txt" >> "%LogFilePath%"
Echo.


