REM Testen van projecten

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\operator

Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t100_network_connect/result_html t100_network_connect
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t101_network_od_pc4_dense/result_html t101_network_od_pc4_dense
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t102_network_od_pc6_sparse/result_html t102_network_od_pc6_sparse
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t200_grid_Poly2Grid/result_html t200_grid_Poly2Grid
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t300_xml_ReadParse/result_html t300_xml_ReadParse
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t301_BAG_ResidentialType/result_html t301_BAG_ResidentialType

REM CalcCache Section, first instance is used to add data to CalcCache, second instance to test if data is in CalcCache
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t400_CalcCache_connect/result_html t400_CalcCache_connect
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %RegressionPath% results/t400_CalcCache_connect/result_html t400_CalcCache_connect

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\Vesta
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %VestaRunPath% t510_indicator_results_test/result_html t510_vesta_indicator_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\Sawec
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %SawecRunPath% Tellingen/t520_sawec_tellingen_results_test/result_html t520_sawec_tellingen_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\LUSDemo
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %LusDemoRunPath% /test/UseReference/t610_lus_demo_results_test/result_html t610_lus_demo_results_test

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\LUSDemo2022
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %LusDemoRunPath2022% t611_lus_demo_2022_results_test/result_html t611_lus_demo_2022_results_test

REM Call Full\RsLight_2021_Instances_WithFileCompare.bat %Setting1% %Setting2% t625_RSLight_2021_ontwikkel_2
Call Full\RsLight_2021_Ontwikkel_3.bat %Setting1% %Setting2% t630_RSLight_2021_ontwikkel_3

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\2UP
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %TwoUPRunPath% test_2UP_indicator_results/result_html_zonder_calcache t710_2UP_indicator_results_zonder_CalCache
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %TwoUPRunPath% test_2UP_indicator_results/result_html_met_calcache    t711_2UP_indicator_results_met_CalCache

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\100m_DynaPop
Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %DynaPopPath% t810_ValLuisa_Czech_LU_POP/result_html t810_ValLuisa_Czech_LU_POP 

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\Storage
Call Full\InstanceTimeStampWithFileCompare.bat %Setting1% %Setting2% %StoragePath% EsriShape/polygon/Write t050_Storage_Write_Shape_Polygon_Folder_Compare  %LocalDataDir%\Regression\Storage\regr_results\polygon\area.* %TstDir%\Storage\data\polygon\area.*

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\BAG20
Call Full\InstanceTimeStampWithFileSizeCompare.bat %Setting1% %Setting2% %BAG20MakeSnapShotPath% snapshot_date_nl_geoparaat_gpkg/result_gpkg/make_geopackage t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare %LocalDataDir%\Regression\BAG20\snapshot_Utrecht_20210701.gpkg %RegressionTestsSourceDataDir%\BAG20\snapshot_Utrecht_20210701.gpkg

