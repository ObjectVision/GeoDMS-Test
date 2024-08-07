Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\RSopen_RegressieTest

Echo.
Echo ************************
Echo Test: %4
Echo LocalDataProjDir: %GEODMS_DIRECTORIES_LOCALDATAPROJDIR%

SET prj=RSopen_RegressieTest
Echo Removing .dmsdata en .fss files from !LocalDataDirRegression!\%prj%

REM If exist del !LocalDataDirRegression!\RSopen_RegressieTest\*.fss
REM If exist del !LocalDataDirRegression!\RSopen_RegressieTest\*.dmsdata

Call full/SetStartTime.bat

Echo.
Echo Sectie PrepareBaseData:
Echo.

Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run1
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run2 
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run3 
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run4 
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run5 
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run6
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run7
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run8
Echo %time% 

Set GeoDmsLogFilePath=%results_log_folder%\t640_1_RSopen_prepare_base_data.txt
del %GeoDmsLogFilePath% 2>nul

Call full/EchoAndExecute.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms WriteBasedata/Generate_Run9
rem pause

Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /t640_1_RSopen_prepare_base_data/result_html

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t640_1_RSopen_prepare_base_data.txt

Call full/SetStartTime.bat

rem pause

Echo.
Echo Sectie MaakVariantData:
Echo.
set VariantDataOntkoppeld=FALSE
set IsProductieRun=FALSE
set RSL_VARIANT_NAME=BAU

Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /WriteVariantData/Zeef_AdminDomain_All
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /WriteVariantData/Opbrengsten_perOP
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /WriteVariantData/Zeef_Domain_All
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /WriteVariantData/Verblijfsrecreatie
Echo %time% 
rem pause

Set GeoDmsLogFilePath=%results_log_folder%\t640_2_RSopen_MakeVariantData.txt
del %GeoDmsLogFilePath% 2>nul

Call full/EchoAndExecute.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /t640_2_RSopen_MakeVariantData/result_html 
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t640_2_RSopen_MakeVariantData.txt

Call full/SetStartTime.bat


Echo.
Echo Sectie Run Model:
Echo.
set VariantDataOntkoppeld=TRUE

Set GeoDmsLogFilePath=%results_log_folder%\t640_3_RSopen_indicator_results_test.txt
del %GeoDmsLogFilePath% 2>nul

Call full/EchoAndExecute.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /Analysis/Allocatie/Zichtjaren/Y2050/Impl/Generate
Echo %time% 
Call full/EchoAndExecuteWithoutLogFile.bat %1 %2 %3 %RSopen_RegressieTestPath%\Regression_test.dms /t640_3_RSopen_indicator_results_test/result_html
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t640_3_RSopen_indicator_results_test.txt


