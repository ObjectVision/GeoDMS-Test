REM Testen van projecten
SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\Storage
Call Full\InstanceTimeStampWithFileCompare.bat %Setting1% %Setting2% %Setting3% %StoragePath% EsriShape/polygon/Write t050_Storage_Write_Shape_Polygon_Folder_Compare  %LocalDataDir%\Regression\Storage\regr_results\polygon\area.* %TstDir%\Storage\data\polygon\area.*
REM SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\BAG20
REM Call Full\InstanceTimeStampWithFileSizeCompare.bat %Setting1% %Setting2% %Setting3% %BAG20MakeSnapShotPath% snapshot_date_nl_geoparaat_gpkg/result_gpkg/make_geopackage t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare %LocalDataDir%\Regression\BAG20\snapshot_Utrecht_20210701.gpkg %RegressionTestsSourceDataDir%\BAG20\snapshot_Utrecht_20210701.gpkg

Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t100_network_connect/result_html t100_network_connect
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t101_network_od_pc4_dense/result_html t101_network_od_pc4_dense
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t102_network_od_pc6_sparse/result_html t102_network_od_pc6_sparse

Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %BLRDConversiePath% t151_conversie_bl_rd_test/result_html t151_conversie_bl_rd_test

Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t200_grid_Poly2Grid/result_html t200_grid_Poly2Grid
SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t300_xml_ReadParse/result_html t300_xml_ReadParse
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %RegressionPath% results/t301_BAG_ResidentialType/result_html t301_BAG_ResidentialType

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\NetworkModel
Call Full\NetworkModel.bat %Setting1% %Setting2% %Setting3% t405_2_NetworkModel_PBL_indicator_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\NetworkModelEU
Call Full\NetworkModelEU.bat %Setting1% %Setting2% %Setting3% t410_NetworkModel_EU_indicator_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\Hestia
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %HestiaRunPath% t530_hestia2024/result_html t530_hestia2024

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\LUSDemo2023
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %LusDemoRunPath2023% t611_lus_demo_2023_results_test/result_html t611_lus_demo_2023_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\RS
Call Full\RSOpen.bat %Setting1% %Setting2% %Setting3% t640_3_RSopen_indicator_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\RS_v2025
Call Full\RSOpen_v2025.bat %Setting1% %Setting2% %Setting3% t641_3_RSopen_indicator_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\2UP
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %TwoUPRunPath% test_2UP_indicator_results/result_html_zonder_calcache t710_2UP_indicator_results_zonder_CalCache
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %TwoUPRunPath% test_2UP_indicator_results/result_html_met_calcache    t711_2UP_indicator_results_met_CalCache

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\2BURP
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %TwoBURPRunPath% t720_2BURP_indicator_results/result t720_2BURP_indicator_results

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\100m_DynaPop
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %DynaPopPath% t810_ValLuisa_Czech_LU_POP/result_html t810_ValLuisa_Czech_LU_POP 

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\Cusa
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %CusaRunPath% t910_cusa2_Africa_test/result_html t910_cusa2_Africa_test
