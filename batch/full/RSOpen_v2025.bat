Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %4
Echo LocalDataProjDir: %GEODMS_DIRECTORIES_LOCALDATAPROJDIR%
Echo RSo_DataDir: %RSo_DataDir%
Echo RSo_PrivDataDir: %RSo_PrivDataDir%

SET prj=RSopen_RegressieTest_v2025

REM ===== Generate BaseData
Call full/SetStartTime.bat

Echo.
Echo Sectie PrepareBaseData:
Echo.

Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath_v2025%\Regression_test.dms WriteBasedata/Generate_Run1

Set GeoDmsLogFilePath=%results_log_folder%\t641_1_RSopen_prepare_base_data.txt
del %GeoDmsLogFilePath% 2>nul

Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath_v2025%\Regression_test.dms /t641_1_RSopen_prepare_base_data/result_html

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t641_1_RSopen_prepare_base_data.txt

REM ===== Generate VariantData
Call full/SetStartTime.bat

Echo.
Echo Sectie MaakVariantData:
Echo.
set VariantDataOntkoppeld=FALSE
set IsProductieRun=FALSE
set RSL_VARIANT_NAME=BAU

Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath_v2025%\Regression_test.dms /WriteVariantData/Generate_Run1
Echo %time% 

Set GeoDmsLogFilePath=%results_log_folder%\t641_2_RSopen_MakeVariantData.txt
del %GeoDmsLogFilePath% 2>nul

Call full/EchoAndExecute.bat %1 %2 %3 %RSopen_RegressieTestPath_v2025%\Regression_test.dms /t641_2_RSopen_MakeVariantData/result_html 
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t641_2_RSopen_MakeVariantData.txt

REM ===== Generate Allocation Results
Call full/SetStartTime.bat

Echo.
Echo Sectie Run Model:
Echo.
set VariantDataOntkoppeld=TRUE

Set GeoDmsLogFilePath=%results_log_folder%\t641_3_RSopen_indicator_results_test.txt
del %GeoDmsLogFilePath% 2>nul

Call full/EchoAndExecute.bat %1 %2 %3 %RSopen_RegressieTestPath_v2025%\Regression_test.dms /Allocatie/Zichtjaren/Y2060/Impl/Generate
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath_v2025%\Regression_test.dms /t641_3_RSopen_indicator_results_test/result_html
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t641_3_RSopen_indicator_results_test.txt


