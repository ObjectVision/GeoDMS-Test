Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\NetworkModel

Echo.
Echo ************************
Echo Test: %4
Echo LocalDataProjDir: %GEODMS_DIRECTORIES_LOCALDATAPROJDIR%

SET prj=networkmodel_pbl_regressietest

REM Echo Removing .dmsdata, .fss, and .csv files from %GEODMS_DIRECTORIES_LOCALDATAPROJDIR%
REM rd /S /Q %GEODMS_DIRECTORIES_LOCALDATAPROJDIR% 2>nul
REM If exist del !LocalDataDirRegression!\networkmodel_pbl_regressietest\*.fss
REM If exist del !LocalDataDirRegression!\networkmodel_pbl_regressietest\*.dmsdata
REM If exist del !LocalDataDirRegression!\networkmodel_pbl_regressietest\Output\PerRegio\*.csv
REM If exist del !LocalDataDirRegression!\networkmodel_pbl_regressietest\Output\PerRegio\*.xml

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

REM ====== ZONDER FENCE (oftewel oude test)==============
Call full/SetStartTime.bat

Echo.
Echo Sectie Run Model:
Echo.

Set GeoDmsLogFilePath=%results_log_folder%\t405_2_NetworkModel_PBL_indicator_results_test.txt
del %GeoDmsLogFilePath% 2>nul
Set UseFence=FALSE

Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %3 %Networkmodel_pbl_regressietest%\main.dms RegressieTest/Step2_1_run_model_tiled_zonderFence 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %3 %Networkmodel_pbl_regressietest%\main.dms RegressieTest/t405_2_NetworkModel_PBL_indicator_results_test/result_html
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t405_2_NetworkModel_PBL_indicator_results_test.txt

REM ====== MET FENCE ==============
Call full/SetStartTime.bat

Echo.
Echo Sectie Run Model:
Echo.

Set GeoDmsLogFilePath=%results_log_folder%\t405_3_NetworkModel_PBL_fenced_indicator_results_test.txt
del %GeoDmsLogFilePath% 2>nul
Set UseFence=TRUE

Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %3 %Networkmodel_pbl_regressietest%\main.dms RegressieTest/Step2_2_run_model_tiled_metFence 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %3 %Networkmodel_pbl_regressietest%\main.dms RegressieTest/t405_3_NetworkModel_PBL_fenced_indicator_results_test/result_html
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t405_3_NetworkModel_PBL_fenced_indicator_results_test.txt


