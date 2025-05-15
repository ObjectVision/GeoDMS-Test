REM Testen van projecten
REM Call Full\RsLight_2021_Instances_WithFileCompare.bat %Setting1% %Setting2% t625_RSLight_2021_ontwikkel_2
REM Call Full\RsLight_2021_Ontwikkel_3.bat %Setting1% %Setting2% t630_RSLight_2021_ontwikkel_3
REM Call Full\RsLight_2021_Ontwikkel_3_compacted_untiled.bat %Setting1% %Setting2% t631_RSLight_2021_ontwikkel_3_compacted_untiledPath
REM Call Full\RsLight_2021_Ontwikkel_3_compacted_untiled_all_true.bat %Setting1% %Setting2% RSLight2021_ontwikkel_3_compacted_untiled_all_truePath
REM Call Full\RsLight_2021_Ontwikkel_3_compacted_untiled_all_true.bat %Setting1% %Setting2% RSLight2021_ontwikkel_3_compacted_untiled_all_truePath

REM SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\RS_v2025
REM SET GEODMS_DIRECTORIES_SOURCEDATADIR=E:\SourceData
REM Call Full\RSOpen_v2025.bat %Setting1% %Setting2% %Setting3% t641_3_RSopen_indicator_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\MetworkModel
Call Full\NetworkModel.bat %Setting1% %Setting2% %Setting3% t405_2_NetworkModel_PBL_indicator_results_test
