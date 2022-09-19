Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %3

SET prj=RSLight2021_ontwikkel_2
SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\%prj%
Echo Removing .dmsdata en .fss files from !LocalDataDirRegression!\%prj%

If exist del !LocalDataDirRegression!\RSLight_2021_ontwikkel_2_\*.fss
If exist del !LocalDataDirRegression!\RSLight_2021_ontwikkel_2_\*.dmsdata

Call full/SetStartTime.bat

Echo.
Echo Sectie PrepareData:
Echo.
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\PrepareData.dms MaakOntkoppeldeBronData/Generate_Run0
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\PrepareData.dms MaakOntkoppeldeBronData/Generate_Run1
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\PrepareData.dms MaakOntkoppeldeBronData/Generate_Run2
Echo %time%
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\PrepareData.dms MaakOntkoppeldeBronData/Generate_Run3 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\PrepareData.dms MaakOntkoppeldeBronData/Generate_Run4 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\PrepareData.dms MaakOntkoppeldeBronData/Generate_PrivData 
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\PrepareData.dms MaakOntkoppeldeBronData/Generate_Run5 
Echo %time% 

Echo.
Echo Sectie Variants:
Echo.
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\hoog_BAU.dms MaakOntkoppeldeLocalData/ExploitatieSaldo_All
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\hoog_BAU.dms MaakOntkoppeldeLocalData/Beschikbaar_All
Echo %time% 

Echo.
Echo Sectie Cases:
Echo.
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\hoog_BAU.dms MaakOntkoppeldeLocalData/AllocatieResultaten_PerYear/Y2030
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\hoog_BAU.dms MaakOntkoppeldeLocalData/AllocatieResultaten_PerYear/Y2040
Echo %time% 
Call full/EchoAndExecute.bat %1 %2 %RSLight_2021Path%\Runs\hoog_BAU.dms MaakOntkoppeldeLocalData/AllocatieResultaten_PerYear/Y2050

Call full/SetEndTime.bat

Set resultfile=%results_folder%\%3.txt
Echo ^<description^>%3%:^<^/description^>^<result^> > %resultfile%

Echo.

Set calc_result_path_part=%prj%\Allocatie\WLO_hoog_BAU
Set ref_result_path_part=%prj%\refResults\Allocatie\WLO_hoog_BAU

Echo %time% 
Call full/EchoAndFileCompare.bat !LocalDataDirRegression!\%calc_result_path_part%\StandY2050.fss\PandFootprint\*.dmsdata !RegressionTestsSourceDataDir!\%ref_result_path_part%\StandY2050.fss\PandFootprint\*.dmsdata %resultfile% StandY2050.fss\PandFootprint
Echo %time% 
Call full/EchoAndFileCompare.bat !LocalDataDirRegression!\%calc_result_path_part%\StandY2050.fss\Werken\*.dmsdata !RegressionTestsSourceDataDir!\%ref_result_path_part%\StandY2050.fss\Werken\*.dmsdata %resultfile% StandY2050.fss\Werken
Echo %time% 
Call full/EchoAndFileCompare.bat !LocalDataDirRegression!\%calc_result_path_part%\StandY2050.fss\Wonen\*.dmsdata !RegressionTestsSourceDataDir!\%ref_result_path_part%\StandY2050.fss\Wonen\*.dmsdata %resultfile% StandY2050.fss\Wonen
Echo %time% 
Call full/EchoAndFileCompare.bat !LocalDataDirRegression!\%calc_result_path_part%\StandY2050.fss\*.dmsdata !RegressionTestsSourceDataDir!\%ref_result_path_part%\StandY2050.fss\*.dmsdata %resultfile% StandY2050.fss
Echo %time% 

Echo ^<^/result^>^ >> %resultfile%

Call full/WriteTimeStamps.bat %resultfile%



