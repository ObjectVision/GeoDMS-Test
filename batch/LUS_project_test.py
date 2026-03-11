import argparse
import os
import sys
from pathlib import Path
import glob
import shutil
import importlib

## input klant

# geodms versie
# sha-1 code
# branch (afleiden?)
# 
# projdir lcoatie
# local dir
# sorucedata dir

### EIND USER PARAMETERS


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
    regression_test_paths["LUSDemo"] = f"C:/projdir/_archief/LandUseModelling/lus_demo/cfg/demo.dms"
    return regression_test_paths

def update_result_folder_paths_with_git_repo() -> dict:
    return

def add_experiment(exps:list, exp_name:str, geodms_cmd:str, result_folder:str, result_folder_name:str, local_machine_parameters:dict, geodms_paths:dict, env_vars, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str, local_git_repo:str=None) -> list:
    # override results_folder with added local_git_repo location if applicable


    regression.add_exp(exps, name=f"{result_folder_name}__{exp_name}", cmd=geodms_cmd, exp_fldr=f"{result_folder}/{result_folder_name}", env=env_vars, log_fn=f"{result_folder}/{result_folder_name}/log/{exp_name}.txt")
    exps 

def get_experiments(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str, local_git_repo:str=None) -> list:
    exps = []

    # set environment variables
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)

    # add LUS demo to experiments
    local_git_repo="C:/projdir/_archief/LandUseModelling"
    result_folder_name = regression.get_result_folder_name(version, geodms_paths, MT1, MT2, MT3, local_git_repo)
    result_paths['results_folder'] = f"{result_paths["results_base_folder"]}/{result_folder_name}"
    result_paths['results_log_folder'] = f"{result_paths["results_base_folder"]}/{result_folder_name}/log"
    result_folder = result_paths["results_base_folder"]
    exp_name="A1_GE_Discr"
    add_experiment(exps=exps, \
                   exp_name=exp_name,
                   geodms_cmd=f"{geodms_paths['GeoDmsRunPath']} /L{result_folder}/{result_folder_name}/log/{exp_name}.txt /{MT1} /{MT2} /{MT3} {regression_test_paths['LUSDemo']} @statistics Final_Results/A1_GE_Discr",
                   result_folder=result_folder,
                   result_folder_name=result_folder_name,
                   local_machine_parameters=local_machine_parameters,
                   geodms_paths=geodms_paths, 
                   env_vars=env_vars, 
                   regression_test_paths=regression_test_paths, 
                   result_paths=result_paths, 
                   version=version, 
                   MT1=MT1, MT2=MT2, MT3=MT3, 
                   local_git_repo=local_git_repo)
    
    #regression.add_exp(exps, name=f"{result_folder_name}__A1_GE_Discr", cmd=f"{geodms_paths['GeoDmsRunPath']} /L{result_folder}/{result_folder_name}/log/A1_GE_Discr.txt /{MT1} /{MT2} /{MT3} {regression_test_paths['LUSDemo']} @statistics Final_Results/A1_GE_Discr", exp_fldr=f"{result_folder}/{result_folder_name}", env=env_vars, log_fn=f"{result_folder}/{result_folder_name}/log/A1_GE_Discr.txt")

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
    result_paths["title"] = "LUS demo test" 
    result_paths["logo"] = "https://themasites.pbl.nl/o/zelfstandig-thuis-hoge-leeftijd/pbl-logo.png" # "https://upload.wikimedia.org/wikipedia/commons/8/88/Logo-TNO.svg"
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
    geodms_paths["GeoDmsProfilerPath"] = "C:/PROGRA~1/ObjectVision/GeoDms19.1.0/profiler.py" #geodms_profiler if geodms_profiler_env_key!=geodms_profiler else f"{geodms_paths["GeoDmsPath"]}/profiler.py" # "C:/Users/Cicada/dev/geodms/branches/geodms_v17/profiler/profiler.py"
    geodms_paths["GeoDmsRegressionPath"] = "C:/PROGRA~1/ObjectVision/GeoDms19.1.0/regression.py"  #f"{geodms_paths["GeoDmsPath"]}/regression.py" #"C:/Users/Cicada/dev/geodms/branches/geodms_v17/profiler/regression.py" 
    geodms_paths["GeoDmsRunPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsRun.exe"
    geodms_paths["GeoDmsGuiQtPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsGuiQt.exe"
    return geodms_paths

def run_project_test(git_repo:str="latest", version:str="19.1.0", MT1="S1", MT2="S2", MT3="S3"):
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

    experiments = get_experiments(local_machine_parameters, geodms_paths, regression_test_paths, result_paths, version, MT1, MT2, MT3, git_repo)
    regression.run_experiments(experiments)
    regression.collect_and_generate_test_results(version, result_paths)

    return

if __name__=="__main__":
    run_project_test()