import argparse
import os
from pathlib import Path
import platform
import importlib
import sys
from packaging.version import Version
import re
import glob

def get_local_machine_parameters() -> dict:
    local_machine_parameters = {}
    # user adaptable
    local_machine_parameters["RegressionTestsSourceDataDir"] = "C:/SourceData/RegressionTests"
    local_machine_parameters["RegressionTestsAltSourceDataDir"] = "E:/SourceData"
    local_machine_parameters["LocalDataDir"] = "C:/LocalData"
    return local_machine_parameters

def get_regression_test_paths(local_machine_parameters:dict) -> dict:
    regression_test_paths = {}
    regression_test_paths["prj_snapshotsDir"] = f"{local_machine_parameters["RegressionTestsSourceDataDir"]}/prj_shapshots"
    regression_test_paths["BatchDir"] = str(os.getcwd()).replace("\\", "/")
    regression_test_paths["TstDir"] = str(Path(regression_test_paths["BatchDir"]).parent.absolute()).replace("\\", "/")

    regression_test_paths["OperatorPath"] = f"{regression_test_paths["TstDir"]}/Operator/cfg/Operator.dms"
    regression_test_paths["StoragePath"] = f"{regression_test_paths["TstDir"]}/Storage/cfg/Regression.dms"
    regression_test_paths["StorageGDALPath"] = f"{regression_test_paths["TstDir"]}/Storage_gdal/cfg/Regression.dms"
    regression_test_paths["RegressionPath"] = f"{regression_test_paths["TstDir"]}/Regression/cfg/stam.dms"
    regression_test_paths["BLRDConversiePath"] = f"{regression_test_paths["prj_snapshotsDir"]}/bl_rd_conversie/cfg/root.dms"

    regression_test_paths["LusDemoRunPath2023"] = f"{regression_test_paths["prj_snapshotsDir"]}/lus_demo_2023/cfg/demo.dns"
    regression_test_paths["RSLRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSL_2020/cfg/regression_test.dms"
    regression_test_paths["RSLight_2020Path"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSLight_2020/cfg/Regression_test.dms"
    regression_test_paths["HestiaRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/Hestia2024/Runs/HestiaRun.dms"

    regression_test_paths["TwoUPRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/2UP/cfg/stam.dms"
    regression_test_paths["TwoBURPRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/2BURP/cfg/stam.dms"
    regression_test_paths["DynaPopPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/100m_DynaPop/cfg/StatusQuo.dms"
    regression_test_paths["RSLight_2021Path"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSLight2021_ontwikkel_2"
    regression_test_paths["RSLight2021_ontwikkel_3Path"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSLight2021_ontwikkel_3"
    regression_test_paths["BAG20MakeSnapShotPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/BAG20/cfg/BAG20_MakeSnaphot.dms"
    regression_test_paths["RSopen_RegressieTestPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/RsOpen_regressietest/cfg"
    regression_test_paths["RSopen_RegressieTestPath_v2025"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSopen_RegressieTest_v2025/cfg"
    regression_test_paths["CusaRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/geodms_africa_cusa2/cfg/africa.dms"
    regression_test_paths["Networkmodel_pbl_regressietest"] = f"{regression_test_paths["prj_snapshotsDir"]}/NetworkModel_PBL_RegressieTest/cfg"
    regression_test_paths["Networkmodel_eu_regressietest"] = f"{regression_test_paths["prj_snapshotsDir"]}/networkmodel_eu_regressieTest/cfg"
    regression_test_paths["RslDataDir"] = f"{local_machine_parameters["RegressionTestsSourceDataDir"]}/RSL"
    regression_test_paths["HestiaDataDir"] = f"{local_machine_parameters["RegressionTestsSourceDataDir"]}/Hestia"
    regression_test_paths["RSo_DataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSOpen"
    regression_test_paths["RSo_PrivDataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSOpen_Priv"

    return regression_test_paths

def get_geodms_paths(version:str) -> dict:
    assert(version)
    geodms_paths = {}
    geodms_paths["GeoDmsPlatform"] = "x64"
    geodms_paths["GeoDmsPath"] = f"C:/PROGRA~1/ObjectVision/GeoDms{version}"
    geodms_paths["GeoDmsProfilerPath"] = "C:/Users/Cicada/dev/geodms/branches/geodms_v17_profilerpy/profiler/Profiler.py"  #f"{geodms_paths["GeoDmsPath"]}/Profiler.py"
    import_module_from_path(geodms_paths["GeoDmsProfilerPath"])

    geodms_paths["GeoDmsRunPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsRun.exe"
    geodms_paths["GeoDmsGuiQtPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsGuiQt.exe"
    return geodms_paths

def get_local_machine_name() -> str:
    return platform.node()

def get_result_folder_name(version:str, geodms_paths:dict, MT1:str, MT2:str, MT3:str) -> str:
    return f"{version.replace(".", "_")}_{geodms_paths["GeoDmsPlatform"]}_SF_{MT1}{MT2}{MT3}_{get_local_machine_name()}"

def get_result_paths(geodms_paths:dict, regression_test_paths:dict, version:str, MT1:str, MT2:str, MT3:str) -> dict:
    result_paths = {}
    result_paths["results_base_folder"] = f"{regression_test_paths["TstDir"]}/Regression/GeoDMSTestResults"
    result_paths["results_folder"] = f"{result_paths["results_base_folder"]}/{get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)}"
    result_paths["results_log_folder"] = f"{result_paths["results_folder"]}/log"
    return result_paths

def import_module_from_path(path):
    module_name = os.path.splitext(os.path.basename(path))[0]  # Extract "module" from "module.py"

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Can't find spec for {module_name} at {path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    globals()[module_name] = module  # Inject into global namespace
    spec.loader.exec_module(module)
    
    return module

def get_full_regression_test_environment_string(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict) -> str:
    full_regression_test_string = ""
    for key in local_machine_parameters:
        value = local_machine_parameters[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"

    for key in geodms_paths:
        value = geodms_paths[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"
    
    for key in regression_test_paths:
        value = regression_test_paths[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"
    
    for key in result_paths:
        value = result_paths[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"

    return full_regression_test_string[1:]

def get_operator_test_experiments(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str) -> list:
    operator_test_experiments = []
    env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    result_folder_name = get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)
    # "C:\Program Files\ObjectVision\GeoDms17.4.6\GeoDmsRun.exe" /L"C:\Users\Cicada\prj\GeoDMS-Test\Regression\GeoDMSTestResults\17_4_6_x64_SF_S1S2S3_OVSRV07\log\t010_operator_test_C1C2C3.txt"  /C1 /C2 /C3 C:\Users\Cicada\prj\GeoDMS-Test\Operator\cfg\Operator.dms results/regression/t010_operator_test/C1C2C3
    #'C:/PROGRA~1/ObjectVision/GeoDms17.4.6/GeoDmsRun.exe /L C:\\Users\\Cicada\\prj\\GeoDMS-Test\\batch/Regression/GeoDMSTestResults/17.4.6_x64_SF_C1C2C3_OVSRV07/log/t010_operator_test_C1C2C3.txt /C1 /C2 /C3 C:\\Users\\Cicada\\prj\\GeoDMS-Test\\batch/Operator/cfg/Operator.dms results/regression/t010_operator_test/stored_result'
    
    operator_test_experiments.append(Profiler.Experiment(name=f"{result_folder_name}__t010_operator_test", \
                                                         command=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t010_operator_test_{MT1}{MT2}{MT3}.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} results/regression/t010_operator_test/stored_result", \
                                                         experiment_folder=f"{result_paths["results_folder"]}", \
                                                         environment_variables=env_vars,\
                                                         cwd=None,\
                                                         geodms_logfile=f"{result_paths["results_log_folder"]}/t010_operator_test_{MT1}{MT2}{MT3}.txt",\
                                                         binary_experiment_file=""))
    
    return operator_test_experiments

def folder_is_results_folder(result_folder_name:str) -> bool:
    pattern = r'^\d+_\d+_\d+_(?:[A-Za-z0-9]+_)*[A-Za-z0-9]+$'
    match = re.match(pattern, result_folder_name)
    return match

def parse_folder_name(result_folder_name:str) -> list:
    major, minor, patch, architecture, sf, multithreading, local_machine_name = result_folder_name.split("_")
    return [major, minor, patch, architecture, sf, multithreading, local_machine_name]

def get_semantic_version_from_folder_name(result_folder_name:str):
    major, minor, patch,_,_,_,_ = parse_folder_name(result_folder_name)
    return f"{major}.{minor}.{patch}"

def get_version_range(valid_result_folders:list) -> tuple:
    newest_tested_geodms_version = get_semantic_version_from_folder_name(valid_result_folders[0])
    oldest_tested_geodms_version = newest_tested_geodms_version
    for result_folder_name in valid_result_folders:
        version = get_semantic_version_from_folder_name(result_folder_name)
        if Version(version) > Version(newest_tested_geodms_version):
            newest_tested_geodms_version = version
        if Version(version) < Version(oldest_tested_geodms_version):
            oldest_tested_geodms_version = version
    return (newest_tested_geodms_version, oldest_tested_geodms_version)

def get_valid_result_folders(version:str, result_paths:dict) -> list:
    valid_result_folders = []
    result_folder_candidates = os.listdir(result_paths["results_base_folder"])
    for candidate in result_folder_candidates:
        if not folder_is_results_folder(candidate):
            continue
        major, minor, patch, architecture, sf, multithreading, local_machine_name = parse_folder_name(candidate)
        if Version(f"{major}.{minor}.{patch}") <= Version(version):
            valid_result_folders.append(candidate)

    return valid_result_folders

def sort_valid_result_folders_new_to_old(valid_result_folders:list) -> list:
    sorted_valid_result_folders = []
    for result_folder in valid_result_folders:
        sorted_valid_result_folders.append((result_folder, Version(get_semantic_version_from_folder_name(result_folder))))
        sorted_valid_result_folders.sort(reverse=True, key=lambda x: x[1])
    return sorted_valid_result_folders

def get_all_experiments_from_experiment_folder(experiment_folder_path:str):
    return glob.glob(f"{experiment_folder_path}/*.bin")

def get_experiment_name_from_experiment_filename(experiment_filename:str) -> str:
    return experiment_filename.split("__")[1][:-4]

def get_all_regression_tests_by_name(result_paths:dict, valid_result_folders:list):
    regression_tests = []
    for result_folder in valid_result_folders:
        experiment_folder_path = f"{result_paths["results_base_folder"]}/{result_folder}"
        experiment_filenames = get_all_experiments_from_experiment_folder(experiment_folder_path)
        for experiment_filename in experiment_filenames:
            experiment_name = get_experiment_name_from_experiment_filename(experiment_filename)
            if experiment_name in regression_tests:
                continue
            regression_tests.append(experiment_name)
    return regression_tests

def collect_experiment_filenames_per_experiment(regression_tests:list, result_paths:dict, sorted_valid_result_folders:list) -> dict:
    regression_tests_experiment_filenames = {}
    for regression_test in regression_tests:
        regression_tests_experiment_filenames[regression_test] = []
        for experiment_folder in sorted_valid_result_folders:
            experiment_folder_path = f"{result_paths["results_base_folder"]}/{experiment_folder}"
            experiment_filenames = get_all_experiments_from_experiment_folder(experiment_folder_path)
            for experiment_filename in experiment_filenames:
                experiment_name = get_experiment_name_from_experiment_filename(experiment_filename)
                if not experiment_name == regression_test:
                    continue
                regression_tests_experiment_filenames.append(f"{experiment_folder_path}/{experiment_filename}")
    return

def collect_experiment_summaries(regression_test_files:dict) -> list[list]:
    
    pass

def collect_and_generate_test_results(version:str, result_paths:dict):
    valid_result_folders = get_valid_result_folders(result_paths)
    version_range = get_version_range(valid_result_folders)
    sorted_valid_result_folders = sort_valid_result_folders_new_to_old(valid_result_folders)
    regression_test_names = get_all_regression_tests_by_name(valid_result_folders)
    regression_test_files = collect_experiment_filenames_per_experiment(regression_test_names, result_paths, sorted_valid_result_folders)
    regression_test_summaries = collect_experiment_summaries(regression_test_files)

    return

def run_full_regression_test(version:str="17.4.6"):
    # arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-version", help="Geodms version ie: 17.4.6")
    parser.add_argument("-MT1", help="Multithreading 1: S1 or C1")
    parser.add_argument("-MT2", help="Multithreading 2: S2 or C2")
    parser.add_argument("-MT3", help="Multithreading 3: S3 or C3")
    parser.add_argument("-pause_when_done", help="Pauses when done with all regression tests")
    args = parser.parse_args()
    
    if args.version:
        version = args.version

    MT1 = args.MT1
    MT2 = args.MT2
    MT3 = args.MT3
    pause_when_done = args.pause_when_done

    # default params
    if not MT1:
        MT1="C1"
    if not MT2:
        MT2="C2"
    if not MT3:
        MT3="C3"
    if not pause_when_done:
        pause_when_done = False

    print(version, MT1, MT2, MT3, pause_when_done)

    local_machine_parameters = get_local_machine_parameters()
    geodms_paths = get_geodms_paths(version)
    regression_test_paths = get_regression_test_paths(local_machine_parameters)
    result_paths = get_result_paths(geodms_paths, regression_test_paths, version, MT1, MT2, MT3)
    
    operator_experiments = get_operator_test_experiments(local_machine_parameters, geodms_paths, regression_test_paths, result_paths, version, MT1, MT2, MT3)
    experiments = Profiler.RunExperiments(operator_experiments)

    collect_and_generate_test_results(version, result_paths)

    return

if __name__=="__main__":
    run_full_regression_test()