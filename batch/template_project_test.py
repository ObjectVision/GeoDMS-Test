import argparse
import os
import sys
from pathlib import Path
import glob
import shutil
import importlib

def import_module_from_path(path):
    module_name = os.path.splitext(os.path.basename(path))[0]  # Extract "module" from "module.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Can't find spec for {module_name} at {path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    globals()[module_name] = module  # Inject into global namespace
    spec.loader.exec_module(module)
    

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

def get_experiments(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str, local_git_repo:str=None) -> list:
    exps = []
    result_folder_name = regression.get_result_folder_name(version, geodms_paths, MT1, MT2, MT3, local_git_repo)
    result_paths['results_folder'] = f"{result_paths["results_base_folder"]}/{result_folder_name}"
    result_paths['results_log_folder'] = f"{result_paths["results_base_folder"]}/{result_folder_name}/log"
    result_folder = result_paths["results_base_folder"]
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.header_stuff_to_be_removed_in_future(local_machine_parameters, result_paths, MT1, MT2, MT3)

    # add experiments
    regression.add_exp(exps, name=f"{result_folder_name}__git_repo_test1", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_folder}/{result_folder_name}/log/t010_operator_test.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} results/regression/t010_operator_test/stored_result", exp_fldr=f"{result_folder}/{result_folder_name}", env=env_vars, log_fn=f"{result_folder}/{result_folder_name}/log/t010_operator_test.txt", indicator_results_file=f"{result_paths["results_folder"]}/t010_operator_test.txt")
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Storage"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__git_repo_test2", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_folder}/{result_folder_name}/log/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["StoragePath"]} EsriShape/polygon/Write", exp_fldr=f"{result_folder}/{result_folder_name}", env=env_vars, log_fn=f"{result_folder}/{result_folder_name}/log/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt", file_comparison=(f"{regression_test_paths["TstDir"]}/Storage/data/polygon/area.*", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/Storage/regr_results/polygon/area.*"))

    #regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/BAG20"
    #env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    #regression.add_exp(exps, name=f"{result_folder_name}__git_repo_test3", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_folder}/{result_folder_name}/log/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["BAG20MakeSnapShotPath"]} snapshot_date_nl_geoparaat_gpkg/result_gpkg/make_geopackage", exp_fldr=f"{result_folder}/{result_folder_name}", env=env_vars, log_fn=f"{result_folder}/{result_folder_name}/log/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt", file_comparison=(f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/BAG20/snapshot_Utrecht_20210701.gpkg", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/BAG20/snapshot_Utrecht_20210701.gpkg"))

    return exps

def remove_local_data_dir_regression(local_data_regression_folder:str):
    files = glob.glob(local_data_regression_folder+"/*")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        else:
            shutil.rmtree(f)
    return

def get_result_paths(geodms_paths:dict, result_base_path:str, version:str, MT1:str, MT2:str, MT3:str) -> dict:
    result_paths = {}
    result_paths["title"] = "Git project test template" 
    result_paths["logo"] = "https://upload.wikimedia.org/wikipedia/commons/8/88/Logo-TNO.svg"
    result_paths["results_base_folder"] = f"{result_base_path}/Regression/GeoDMSProjectTestResults"
    result_paths["results_folder"] = f"{result_paths["results_base_folder"]}/{regression.get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)}"
    result_paths["results_log_folder"] = f"{result_paths["results_folder"]}/log"
    return result_paths

def get_geodms_paths(version:str) -> dict:
    assert(version)
    geodms_profiler_env_key = f"%GeodmsProfiler%"
    geodms_profiler = os.path.expandvars(geodms_profiler_env_key)
    geodms_paths = {}
    geodms_paths["GeoDmsPlatform"] = "x64"
    geodms_paths["GeoDmsPath"] = f"\"{os.path.expandvars(f"%ProgramFiles%/ObjectVision/GeoDms{version}")}\""
    geodms_paths["GeoDmsProfilerPath"] = "C:/Users/Cicada/dev/geodms/branches/geodms_v17/profiler/profiler.py" #geodms_profiler if geodms_profiler_env_key!=geodms_profiler else f"{geodms_paths["GeoDmsPath"]}/profiler.py"
    geodms_paths["GeoDmsRegressionPath"] = "C:/Users/Cicada/dev/geodms/branches/geodms_v17/profiler/regression.py" #"C:/Users/Cicada/dev/geodms/branches/geodms_v17_profilerpy/profiler/regression.py" #f"{geodms_paths["GeoDmsPath"]}/regression.py"
    geodms_paths["GeoDmsRunPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsRun.exe"
    geodms_paths["GeoDmsGuiQtPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsGuiQt.exe"
    return geodms_paths

def run_project_test(git_repo:str="latest", version:str="17.9.6", MT1="S1", MT2="S2", MT3="S3"):
    parser = argparse.ArgumentParser()
    parser.add_argument("-git_repo", help="Path to local git repo")
    parser.add_argument("-version", help="Geodms version ie: 17.4.6")
    parser.add_argument("-MT1", help="Multithreading 1: S1 or C1")
    parser.add_argument("-MT2", help="Multithreading 2: S2 or C2")
    parser.add_argument("-MT3", help="Multithreading 3: S3 or C3")
    args = parser.parse_args()

    if args.git_repo:
        git_repo = args.git_repo

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
    import_module_from_path(geodms_paths["GeoDmsRegressionPath"])
    regression.import_module_from_path(geodms_paths["GeoDmsProfilerPath"])

    regression_test_paths = get_regression_test_paths(local_machine_parameters)
    result_paths = get_result_paths(geodms_paths, regression_test_paths["TstDir"], version, MT1, MT2, MT3)
    remove_local_data_dir_regression(local_machine_parameters["LocalDataDirRegression"])
    #import_module_from_path(geodms_paths["GeoDmsProfilerPath"])
    

    full_test_experiments = get_experiments(local_machine_parameters, geodms_paths, regression_test_paths, result_paths, version, MT1, MT2, MT3, git_repo)
    regression.run_experiments(full_test_experiments)
    regression.collect_and_generate_test_results(version, result_paths)

    return

if __name__=="__main__":
    run_project_test()