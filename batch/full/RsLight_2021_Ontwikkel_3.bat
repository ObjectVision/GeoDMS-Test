Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\rslight2021_ontwikkel_3

Echo.
Echo ************************
Echo Test: %3
Echo LocalDataProjDir: %GEODMS_DIRECTORIES_LOCALDATAPROJDIR%

SET prj=RSLight2021_ontwikkel_3
Echo Removing .dmsdata en .fss files from !LocalDataDirRegression!\%prj%

If exist del !LocalDataDirRegression!\RSLight_2021_ontwikkel_3_\*.fss
If exist del !LocalDataDirRegression!\RSLight_2021_ontwikkel_3_\*.dmsdata

Call full/SetStartTime.bat

Echo.
Echo Sectie PrepareBaseData:
Echo.
REM Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_PrivData   REM Dit staat gegenereerd in de SD/PrivData, en waarschijnlijk niet nodig om te draaien.

Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run1
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run2 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run3 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run4 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run5 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run6
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run7
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms MaakBasedata/Generate_Run8

Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\PrepareBaseData.dms t630_1_RSLight_2021_ontwikkel_3_prepare_base_data/result_html

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t630_1_RSLight_2021_ontwikkel_3_prepare_base_data.txt

Call full/SetStartTime.bat

rem pause

Echo.
Echo Sectie MaakVariantData:
Echo.
set VariantDataOntkoppeld=FALSE
set IsProductieRun=FALSE
set RSL_VARIANT_NAME=BAU

Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /MaakVariantData/Restricties_All
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /MaakVariantData/Stimuli_All
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /MaakVariantData/Zeef_AdminDomain_All
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /MaakVariantData/Opbrengsten_perOP
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /MaakVariantData/Zeef_Domain_All
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /MaakVariantData/Zeef_perOP
Echo %time% 


Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /MaakVariantData/t630_2_RSLight_2021_ontwikkel_3_MakeVariantData/result_html 
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t630_2_RSLight_2021_ontwikkel_3_MakeVariantData.txt

Call full/SetStartTime.bat

Echo.
Echo Sectie Run Model:
Echo.
set VariantDataOntkoppeld=TRUE

Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /Analysis/Allocatie/Zichtjaren/Y2050/Impl/Generate
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight2021_ontwikkel_3Path%\Runs\casus.dms /RegressieTestIndicatoren/t630_3_RSLight_2021_ontwikkel_3_indicator_results_test/result_html
Echo %time% 

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t630_3_RSLight_2021_ontwikkel_3_indicator_results_test.txt


