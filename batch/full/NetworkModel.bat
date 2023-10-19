Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\NetWorkModel

Echo.
Echo ************************
Echo Test: %4
Echo LocalDataProjDir: %GEODMS_DIRECTORIES_LOCALDATAPROJDIR%

SET prj=networkmodel_pbl_regressietest
Echo Removing .dmsdata en .fss files from !LocalDataDirRegression!\%prj%

If exist del !LocalDataDirRegression!\networkmodel_pbl_regressietest\*.fss
If exist del !LocalDataDirRegression!\networkmodel_pbl_regressietest\*.dmsdata

Call full/SetStartTime.bat

Echo.
Echo Sectie PrepareBaseData:
Echo.

Set GeoDmsLogFilePath=%results_log_folder%\t405_1_NetworkModel_PBL_prepare_data.txt
del %GeoDmsLogFilePath% 2>nul

Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %3 %Networkmodel_pbl_regressietest%\main.dms RegressieTest/Step1_prepare_data 
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %Networkmodel_pbl_regressietest%\main.dms RegressieTest/t405_1_NetworkModel_PBL_prepare_data/result_html
rem pause
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t405_1_NetworkModel_PBL_prepare_data.txt

rem pause


Call full/SetStartTime.bat

Echo.
Echo Sectie Run Model:
Echo.

Set GeoDmsLogFilePath=%results_log_folder%\t405_2_NetworkModel_PBL_indicator_results_test.txt
del %GeoDmsLogFilePath% 2>nul

Call full/EchoAndExecute.bat %1 %2 %3 %Networkmodel_pbl_regressietest%\main.dms RegressieTest/t405_2_NetworkModel_PBL_indicator_results_test/result_html 
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t405_2_NetworkModel_PBL_indicator_results_test.txt


