import argparse
import os
import sys
from pathlib import Path
import glob
import shutil
import importlib
import subprocess
from urllib.parse import urlparse

## START INPUT PARAMETERS
geodms_versie           = "19.1.0"
git_repository_url      = "https://github.com/ObjectVision/LandUseModelling.git"
sha_1                   = "4c99494" 
projdir                 = "C:/LocalData/test_tmp" #hier worden temporary de git repos gecloned, en worden de resultaten weggeschreven. Deze folder wordt niet automatisch verwijderd dus kan later nog bekeken worden.
localdatadir            = "C:/LocalData"
sourcedatadir           = "E:/SourceData/RSopen"
testdir                 = "C:/LocalData/RSOpen_test"

regression_test_paths["VariantDataOntkoppeld"] = "FALSE"
regression_test_paths["IsProductieRun"] = "FALSE"
regression_test_paths["RSL_VARIANT_NAME"] = "BAU"
regression_test_paths["AlleenEindjaar"] = "FALSE"

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
    local_machine_parameters["SourceDataDir"] = sourcedatadir
    local_machine_parameters["GEODMS_OVERRIDABLE_RSO_DataDir"] = sourcedatadir
    local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"] = localdatadir
    return local_machine_parameters

def update_result_folder_paths_with_git_repo() -> dict:
    return

def add_experiment(exps:list, exp_name:str, geodms_cmd:str, result_folder:str, result_folder_name:str, local_machine_parameters:dict, geodms_paths:dict, env_vars, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str, local_git_repo:str=None) -> list:
    # override results_folder with added local_git_repo location if applicable
    regression.add_exp(exps, name=f"{result_folder_name}__{exp_name}", cmd=geodms_cmd, exp_fldr=f"{result_folder}/{result_folder_name}", env=env_vars, log_fn=f"{result_folder}/{result_folder_name}/log/{exp_name}.txt")
    exps 

def get_experiments(local_machine_parameters:dict, geodms_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str, local_git_repo:str=None) -> list:
    exps = []

    # set environment variables
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, {}, result_paths)

    # add LUS demo to experiments
    #local_git_repo="C:/projdir/_archief/LandUseModelling"
    result_folder_name = regression.get_result_folder_name(version, geodms_paths, MT1, MT2, MT3, local_git_repo)
    result_paths['results_folder'] = f"{testdir}/{result_folder_name}"
    result_paths['results_log_folder'] = f"{testdir}/{result_folder_name}/log"
    result_folder = testdir
    exp_name="A1_GE_Discr"
    add_experiment(exps=exps, \
                   exp_name=exp_name,
                   geodms_cmd=f"{geodms_paths['GeoDmsRunPath']} /L{result_folder}/{result_folder_name}/log/{exp_name}.txt /{MT1} /{MT2} /{MT3} {local_git_repo}/lus_demo/cfg/demo.dms @statistics Final_Results/A1_GE_Discr",
                   result_folder=result_folder,
                   result_folder_name=result_folder_name,
                   local_machine_parameters=local_machine_parameters,
                   geodms_paths=geodms_paths, 
                   env_vars=env_vars, 
                   regression_test_paths={}, 
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

def get_result_paths(geodms_paths:dict, version:str, MT1:str, MT2:str, MT3:str) -> dict:
    result_paths = {}
    result_paths["title"] = "RSopen test" 
    result_paths["logo"] = "https://themasites.pbl.nl/o/zelfstandig-thuis-hoge-leeftijd/pbl-logo.png" 
    result_paths["results_base_folder"] = testdir
    result_paths["results_folder"] = f"{testdir}/{regression.get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)}"
    result_paths["results_log_folder"] = f"{result_paths["results_folder"]}/log"
    return result_paths

def get_geodms_paths(version:str) -> dict:
    assert(version)
    geodms_profiler_env_key = f"%GeodmsProfiler%"
    geodms_profiler = os.path.expandvars(geodms_profiler_env_key)
    geodms_paths = {}
    geodms_paths["GeoDmsPlatform"] = "x64"
    geodms_paths["GeoDmsPath"] = f"\"{os.path.expandvars(f"%ProgramFiles%/ObjectVision/GeoDms{version}")}\""
    geodms_paths["GeoDmsProfilerPath"] = f"C:/PROGRA~1/ObjectVision/GeoDms{version}/profiler.py" 
    geodms_paths["GeoDmsRegressionPath"] = f"C:/PROGRA~1/ObjectVision/GeoDms{version}/regression.py"  
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
    result_paths = get_result_paths(geodms_paths, version, MT1, MT2, MT3)
   ## remove_local_data_dir_regression(local_machine_parameters["LocalDataDirRegression"])

    experiments = get_experiments(local_machine_parameters, geodms_paths, result_paths, version, MT1, MT2, MT3, git_repo)
    regression.run_experiments(experiments)
    regression.collect_and_generate_test_results(version, result_paths)

    return

def clone_gitrepo_sha1(git_repository_url: str, sha_1: str, projdir: str):
    if not git_repository_url or not git_repository_url.strip():
        raise ValueError("git_repository_url must be a non-empty string")
    if not sha_1 or not sha_1.strip():
        raise ValueError("sha_1 must be a non-empty string")
    if not projdir or not projdir.strip():
        raise ValueError("projdir must be a non-empty string")

    git_repository_url = git_repository_url.strip()
    sha_1 = sha_1.strip()

    # Create projdir recursively if needed.
    parent_dir = Path(projdir).expanduser().resolve()
    parent_dir.mkdir(parents=True, exist_ok=True)

    # Derive repository name from URL.
    # Works for e.g.
    # - https://github.com/user/repo.git
    # - https://github.com/user/repo
    # - git@github.com:user/repo.git
    repo_part = git_repository_url.rstrip("/")

    if repo_part.endswith(".git"):
        repo_part = repo_part[:-4]

    if "://" in repo_part:
        parsed = urlparse(repo_part)
        git_repository_name = Path(parsed.path).name
    else:
        # Handle SCP-like SSH syntax: git@host:user/repo
        git_repository_name = Path(repo_part.split(":")[-1]).name

    if not git_repository_name:
        raise ValueError(
            f"Could not determine repository name from URL: {git_repository_url}"
        )

    clone_dir = parent_dir / f"{git_repository_name}_{sha_1}"

    if not clone_dir.exists():
        def run_git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
            try:
                return subprocess.run(
                    ["git", *args],
                    cwd=str(cwd) if cwd else None,
                    check=True,
                    text=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.strip() if e.stderr else ""
                stdout = e.stdout.strip() if e.stdout else ""
                msg = f"Git command failed: git {' '.join(args)}"
                if stderr:
                    msg += f"\nstderr: {stderr}"
                if stdout:
                    msg += f"\nstdout: {stdout}"
                raise RuntimeError(msg) from e
            except FileNotFoundError as e:
                raise RuntimeError("git executable not found in PATH") from e

        # Clone first, then check out the requested commit.
        # This reliably supports short SHAs as long as the commit is reachable after clone.
        run_git("clone", git_repository_url, str(clone_dir))
        run_git("checkout", sha_1, cwd=clone_dir)

    return str(clone_dir).replace("\\", "/")

def run_project_test_from_user_input():
    git_repo = clone_gitrepo_sha1(git_repository_url, sha_1, projdir)
    run_project_test(git_repo=git_repo, version=geodms_versie)

if __name__=="__main__":
    #run_project_test()
    run_project_test_from_user_input()