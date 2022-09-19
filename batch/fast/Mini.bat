Rem Mini Test voor specfieke regressie testen

Set ResultFile=%LocalDataDirRegression%\operator\regr_results\mini.txt
if exist del %ResultFile%

Echo GeoDMS Command: %GeoDmsRunCmdBase% "%TstDir%\Operator\cfg\tst.dms" /RegressieTest/tests_log TO %LogFilePath%
Echo. 

%GeoDmsRunCmdBase% "%TstDir%\Operator\cfg\tst.dms" /RegressieTest/tests_log >> "%LogFilePath%"
Echo.  >> "%LogFilePath%"

Rem vergelijk resultaten met wat referentie waarde
Echo File Compare: fc %ResultFile% "%TstDir%\norm\true.txt" to %LogFilePath%
fc "%ResultFile%" "%TstDir%\norm\true.txt" >> "%LogFilePath%"
Echo.

