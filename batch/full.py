import argparse
import os
from pathlib import Path
from generic.regression import *
import glob
import shutil

def get_local_machine_parameters() -> dict:
    local_machine_parameters = {}
    # user adaptable
    #local_machine_parameters["SourceDataDir"] = "E:/SourceData"
    local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"] = "C:/SourceData/RegressionTests"
    local_machine_parameters["RegressionTestsAltSourceDataDir"] = "D:/SourceData"
    local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"] = "C:/LocalData"

    # derived
    local_machine_parameters["LocalDataDirRegression"] = f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/regression"
    local_machine_parameters["tmpFileDir"] = f"{local_machine_parameters["LocalDataDirRegression"]}/log"
    return local_machine_parameters

def get_regression_test_paths(local_machine_parameters:dict) -> dict:
    regression_test_paths = {}
    regression_test_paths["prj_snapshotsDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/prj_snapshots"
    regression_test_paths["BatchDir"] = str(os.getcwd()).replace("\\", "/")
    regression_test_paths["TstDir"] = str(Path(regression_test_paths["BatchDir"]).parent.absolute()).replace("\\", "/")

    regression_test_paths["OperatorPath"] = f"{regression_test_paths["TstDir"]}/Operator/cfg/Operator.dms"
    regression_test_paths["StoragePath"] = f"{regression_test_paths["TstDir"]}/Storage/cfg/Regression.dms"
    regression_test_paths["StorageGDALPath"] = f"{regression_test_paths["TstDir"]}/Storage_gdal/cfg/Regression.dms"
    regression_test_paths["RegressionPath"] = f"{regression_test_paths["TstDir"]}/Regression/cfg/stam.dms"
    regression_test_paths["BLRDConversiePath"] = f"{regression_test_paths["prj_snapshotsDir"]}/bl_rd_conversie/cfg/root.dms"

    regression_test_paths["LusDemoRunPath2023"] = f"{regression_test_paths["prj_snapshotsDir"]}/lus_demo_2023/cfg/demo.dms"
    regression_test_paths["RSLRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSL_2020/cfg/regression_test.dms"
    regression_test_paths["RSLight_2020Path"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSLight_2020/cfg/Regression_test.dms"
    regression_test_paths["HestiaRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/Hestia2024/Runs/HestiaRun.dms"

    regression_test_paths["TwoUPRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/2UP/cfg/stam.dms"
    regression_test_paths["TwoBURPRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/2BURP/cfg/main.dms"
    regression_test_paths["DynaPopPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/100m_DynaPop/cfg/StatusQuo.dms"
    regression_test_paths["RSLight_2021Path"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSLight2021_ontwikkel_2"
    regression_test_paths["RSLight2021_ontwikkel_3Path"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSLight2021_ontwikkel_3"
    regression_test_paths["BAG20MakeSnapShotPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/BAG20/cfg/BAG20_MakeSnaphot.dms"
    regression_test_paths["RSopen_RegressieTestPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/RsOpen_regressietest/cfg"
    regression_test_paths["RSopen_RegressieTestPath_v2025"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSopen_RegressieTest_v2025/cfg"
    regression_test_paths["CusaRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/geodms_africa_cusa2/cfg/africa.dms"
    regression_test_paths["Networkmodel_pbl_regressietest"] = f"{regression_test_paths["prj_snapshotsDir"]}/NetworkModel_PBL_RegressieTest/cfg"
    regression_test_paths["Networkmodel_eu_regressietest"] = f"{regression_test_paths["prj_snapshotsDir"]}/networkmodel_eu_regressieTest/cfg"
    regression_test_paths["GEODMS_Overridable_RslDataDir"] = "F:/SourceData/RSL" #f"{local_machine_parameters["RegressionTestsSourceDataDir"]}/RSL"
    regression_test_paths["GEODMS_Overridable_HestiaDataDir"] = "E:/SourceData/SD51/" #f"{local_machine_parameters["RegressionTestsSourceDataDir"]}/compact_data/Hestia"
    regression_test_paths["GEODMS_Overridable_RSo_DataDir"] = "F:/SourceData/RSopen" #"E:/SourceData/RSOpen"
    regression_test_paths["GEODMS_Overridable_RVF_DataDir"] = "C:/Users/Cicada/OneDrive - Objectvision/Object Vision - SourceData/RS_Friesland" #"C:/Users/Cicada/SourceData/Objectvision/Object Vision - RS_Friesland" #"F:/SourceData/RS_Friesland"
    regression_test_paths["GEODMS_Overridable_RSo_PrivDataDir"] = "F:/SourceData/RSOpen_Priv" # "E:/SourceData/RSOpen_Priv"
    regression_test_paths["GEODMS_Overridable_PrivDataDir"] = "F:/SourceData/RSOpen_Priv"
    regression_test_paths["GEODMS_Overridable_ToBURPDataDir"] = "E:/SourceData/2BURP"
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = local_machine_parameters["LocalDataDirRegression"]
    regression_test_paths["GEODMS_Overridable_MondiaalDataDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/2UP"
    regression_test_paths["GEODMS_Overridable_NetworkModel_Dir"] = f"C:/SourceData/RegressionTests/NetworkModel_regressietest" #E:/SourceData/RegressionTests/NetworkModel_regressietest"
    regression_test_paths["GEODMS_Overridable_NetworkModelDataDir"] = f"C:/SourceData/RegressionTests/NetworkModel_EU_RegressionTest" #f"E:/SourceData/RegressionTests/NetworkModel_EU_regressiontest"
    return regression_test_paths

def get_experiments(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str) -> list:
    exps = []
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    result_folder_name = get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)

    # add experiments
    add_exp(exps, name=f"{result_folder_name}__t010_operator_test", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t010_operator_test.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} results/regression/t010_operator_test/stored_result", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t010_operator_test.txt")
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Storage"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t050_Storage_Write_Shape_Polygon_Folder_Compare", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["StoragePath"]} EsriShape/polygon/Write", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt", file_comparison=(f"{regression_test_paths["TstDir"]}/Storage/data/polygon/area.*", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/Storage/regr_results/polygon/area.*"))

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/BAG20"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["BAG20MakeSnapShotPath"]} snapshot_date_nl_geoparaat_gpkg/result_gpkg/make_geopackage", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt", file_comparison=(f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/BAG20/snapshot_Utrecht_20210701.gpkg", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/BAG20/snapshot_Utrecht_20210701.gpkg"))
    add_exp(exps, name=f"{result_folder_name}__t100_network_connect", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t100_network_connect.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t100_network_connect/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t100_network_connect.txt")
    add_exp(exps, name=f"{result_folder_name}__t101_network_od_pc4_dense", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t101_network_od_pc4_dense.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t101_network_od_pc4_dense/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t101_network_od_pc4_dense.txt")
    add_exp(exps, name=f"{result_folder_name}__t102_network_od_pc6_sparse", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t102_network_od_pc6_sparse.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t102_network_od_pc6_sparse/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t102_network_od_pc6_sparse.txt")
    add_exp(exps, name=f"{result_folder_name}__t151_conversie_bl_rd_test", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t151_conversie_bl_rd_test.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["BLRDConversiePath"]} t151_conversie_bl_rd_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t151_conversie_bl_rd_test.txt")
    add_exp(exps, name=f"{result_folder_name}__t200_grid_Poly2Grid", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t200_grid_Poly2Grid.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t200_grid_Poly2Grid/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t200_grid_Poly2Grid.txt")

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t300_xml_ReadParse", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t300_xml_ReadParse.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t300_xml_ReadParse/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t300_xml_ReadParse.txt")
    add_exp(exps, name=f"{result_folder_name}__t301_BAG_ResidentialType", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t301_BAG_ResidentialType.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t301_BAG_ResidentialType/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t301_BAG_ResidentialType.txt")

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/NetworkModel"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t405_1_NetworkModel_PBL_prepare_data", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_1_NetworkModel_PBL_prepare_data.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step1_prepare_data", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_1_NetworkModel_PBL_prepare_data.txt")

    regression_test_paths["UseFence"] = "FALSE"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t405_2_NetworkModel_PBL_zonderFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_2_NetworkModel_PBL_zonderFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step2_1_run_model_tiled_zonderFence", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_2_NetworkModel_PBL_zonderFence.txt")
    add_exp(exps, name=f"{result_folder_name}__t405_2_2_NetworkModel_PBL_indicator_zonderFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_2_2_NetworkModel_PBL_indicator_zonderFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/t405_2_NetworkModel_PBL_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_2_2_NetworkModel_PBL_indicator_zonderFence.txt", store_results=False)
    
    regression_test_paths["UseFence"] = "TRUE"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t405_3_NetworkModel_PBL_metFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_3_NetworkModel_PBL_metFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step2_2_run_model_tiled_metFence", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_3_NetworkModel_PBL_metFence.txt")
    add_exp(exps, name=f"{result_folder_name}__t405_3_2_NetworkModel_PBL_indicator_metFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_3_2_NetworkModel_PBL_indicator_metFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/t405_3_NetworkModel_PBL_fenced_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_3_2_NetworkModel_PBL_indicator_metFence.txt", store_results=False)

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/networkmodel_eu_regressietest"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t410_NetworkModel_EU", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t410_NetworkModel_EU.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_eu_regressietest"]}/main.dms RegressieTest/t410_NetworkModel_EU_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t410_NetworkModel_EU.txt")

    #regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Hestia"
    #env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    #add_exp(exps, name=f"{result_folder_name}__t530_Hestia_2024", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t530_hestia2024.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["HestiaRunPath"]} t530_hestia2024/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t530_hestia2024.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/LUSDemo2023"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t611_Lus_demo_2023", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t611_Lus_demo_2023.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["LusDemoRunPath2023"]} t611_lus_demo_2023_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t611_Lus_demo_2023.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/RSopen_RegressieTest_v2025"
    regression_test_paths["AlleenEindjaar"] = "TRUE"
    #regression_test_paths["VariantDataOntkoppeld"] = "TRUE"
    #env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    #add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_indicator_results_test_Generate", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_Generate.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath"]}/Regression_test.dms Analysis/Allocatie/Zichtjaren/Y2050/Impl/Generate", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_Generate.txt")
    #add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_indicator_results_test_result_html", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_result_html.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath"]}/Regression_test.dms t640_3_RSopen_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_result_html.txt")
    regression_test_paths["VariantDataOntkoppeld"] = "FALSE"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t641_1_RSopen_MakeBaseData", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_1_RSopen_MakeBaseData.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms WriteBasedata/Generate_Run1", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_1_RSopen_MakeBaseData.txt")
    add_exp(exps, name=f"{result_folder_name}__t641_1_2_RSopen_prepare_base_data_indicator", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_1_2_RSopen_prepare_base_data_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms /t641_1_RSopen_MakeBaseData/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_1_2_RSopen_prepare_base_data_indicator.txt", store_results=False)
    
    regression_test_paths["VariantDataOntkoppeld"] = "FALSE"
    regression_test_paths["IsProductieRun"] = "FALSE"
    regression_test_paths["RSL_VARIANT_NAME"] = "BAU"
    regression_test_paths["AlleenEindjaar"] = "TRUE"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t641_2_RSopen_MakeVariantData", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms WriteVariantData/Generate_Run1", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData.txt")
    add_exp(exps, name=f"{result_folder_name}__t641_2_RSopen_MakeVariantData_indicator", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms t641_2_RSopen_MakeVariantData/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData_indicator.txt", store_results=False)

    regression_test_paths["VariantDataOntkoppeld"] = "TRUE"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_Allocatie", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_Allocatie.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms Allocatie/Zichtjaren/Y2060/Impl/Generate", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_Allocatie.txt")
    add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_indicator_indicator",  cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms t641_3_RSopen_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_indicator.txt", store_results=False)

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/2UP"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t710_2UP", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t710_2UP.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["TwoUPRunPath"]} test_2UP_indicator_results/result_html_zonder_calcache", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t710_2UP.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/2BURP"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t720_2BURP", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t720_2BURP.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["TwoBURPRunPath"]} t720_2BURP_indicator_results/result", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t720_2BURP.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/100m_DynaPop"
    regression_test_paths["GEODMS_Overridable_SourceDataProjDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}"
    #regression_test_paths["GEODMS_Overridable_RunRegions"] = "JrcRegion"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t810_ValLuisa", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t810_ValLuisa.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["DynaPopPath"]} t810_ValLuisa_Czech_LU_POP/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t810_ValLuisa.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Cusa"
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    add_exp(exps, name=f"{result_folder_name}__t910_Cusa2_Africa", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t910_Cusa2_Africa.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["CusaRunPath"]} t910_cusa2_Africa_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t910_Cusa2_Africa.txt")


    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/gui"
    add_exp(exps, name=f"{result_folder_name}__t1630_expandtest", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1630_expandtest.txt /T{regression_test_paths["TstDir"]}/dmsscript/RSLight_2020_expand_S1S2.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["RSLight_2020Path"]} t1630_expandtest_S1S2", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1630_expandtest.txt")
    add_exp(exps, name=f"{result_folder_name}__t1640_value_info", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1640_value_info.txt /T{regression_test_paths["TstDir"]}/dmsscript/value_info.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} t1640_value_info", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1640_value_info.txt")
    add_exp(exps, name=f"{result_folder_name}__t1642_value_info_group_by", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1642_value_info_group_by.txt /T{regression_test_paths["TstDir"]}/dmsscript/value_info_group_by.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["TstDir"]}/operator/cfg/MicroTst.dms t1642_value_info_group_by", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1642_value_info_group_by.txt")

    generated_statfile = f"{local_machine_parameters["tmpFileDir"]}/t1742_command_statistics_stat.html"
    reference_statfile = f"{regression_test_paths["TstDir"]}/norm/Statistics_AUAA.html"
    add_exp(exps, name=f"{result_folder_name}__t1742_command_statistics", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t1742_command_statistics.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} @statistics /Arithmetics/UnTiled/add/attr @file {generated_statfile}", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1742_command_statistics.txt", file_comparison=(reference_statfile, generated_statfile))
    return exps

def remove_local_data_dir_regression(local_data_regression_folder:str):
    files = glob.glob(local_data_regression_folder+"/*")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        else:
            shutil.rmtree(f)
    return

def run_full_regression_test(version:str="17.9.6", MT1="S1", MT2="S2", MT3="S3"): #"17.4.6"):
    parser = argparse.ArgumentParser()
    parser.add_argument("-version", help="Geodms version ie: 17.4.6")
    parser.add_argument("-MT1", help="Multithreading 1: S1 or C1")
    parser.add_argument("-MT2", help="Multithreading 2: S2 or C2")
    parser.add_argument("-MT3", help="Multithreading 3: S3 or C3")
    args = parser.parse_args()
    
    if args.version:
        version = args.version

    if args.MT1:
        MT1 = args.MT1
    if args.MT2:
        MT2 = args.MT2
    if args.MT3:
        MT3 = args.MT3

    print(version, MT1, MT2, MT3)

    local_machine_parameters = get_local_machine_parameters()
    geodms_paths = get_geodms_paths(version)
    regression_test_paths = get_regression_test_paths(local_machine_parameters)
    result_paths = get_result_paths(geodms_paths, regression_test_paths, version, MT1, MT2, MT3)
    remove_local_data_dir_regression(local_machine_parameters["LocalDataDirRegression"])
    import_module_from_path(geodms_paths["GeoDmsProfilerPath"])

    header_stuff_to_be_removed_in_future(local_machine_parameters, result_paths, MT1, MT2, MT3)

    operator_experiments = get_experiments(local_machine_parameters, geodms_paths, regression_test_paths, result_paths, version, MT1, MT2, MT3)
    run_experiments(operator_experiments)

    collect_and_generate_test_results(version, result_paths)

    return

if __name__=="__main__":
    run_full_regression_test()