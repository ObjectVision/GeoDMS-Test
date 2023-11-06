Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\networkmodel_eu_regressietest

Echo.
Echo ************************
Echo Test: %4
Echo LocalDataProjDir: %GEODMS_DIRECTORIES_LOCALDATAPROJDIR%

SET prj=networkmodel_eu_regressietest
Echo Removing .dmsdata en .fss files from !LocalDataDirRegression!\%prj%

If exist del !LocalDataDirRegression!\networkmodel_eu_regressietest\*.fss
If exist del !LocalDataDirRegression!\networkmodel_eu_regressietest\*.dmsdata

Call full/SetStartTime.bat

Echo.
Echo Run Model:
Echo.

Set GeoDmsLogFilePath=%results_log_folder%\t410_NetworkModel_EU_indicator_results_test.txt
del %GeoDmsLogFilePath% 2>nul

Call full/EchoAndExecute.bat %1 %2 %3 %networkmodel_eu_regressietest%\main.dms /RegressieTest/t410_NetworkModel_EU_indicator_results_test/result_html
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t410_NetworkModel_EU_indicator_results_test.txt
