import argparse
import json
import os
import re
import sys
from pathlib import Path
import importlib
import importlib.util
#from generic.regression import *
import glob
import shutil

def import_module_from_path(path):
    module_name = os.path.splitext(os.path.basename(path))[0]  # Extract "module" from "module.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Can't find spec for {module_name} at {path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    globals()[module_name] = module  # Inject into global namespace
    spec.loader.exec_module(module)

# Machine-specific paths live in batch/local_settings.json (gitignored).
# A template is committed as batch/local_settings.json.template — copy it
# to local_settings.json once per working copy and adjust drive letters /
# user names. Each key may also be overridden via an environment variable
# of the same name (env wins over file wins over built-in default).
_BUILT_IN_DEFAULTS = {
    "RegressionTestsSourceDataDir": "C:/SourceData/RegressionTests",
    "RegressionTestsAltSourceDataDir": "D:/SourceData",
    "SourceDataDir": "",  # if blank, derived from RegressionTestsSourceDataDir
    "LocalDataDir": "C:/LocalData",
    "ProfilerDir": str(Path(__file__).resolve().parent.parent.parent / "GeoDMS" / "profiler").replace("\\", "/"),
    "LocalBuildDir": str(Path(__file__).resolve().parent.parent.parent / "GeoDMS" / "build" / "windows-x64-release" / "bin").replace("\\", "/"),
    "LocalBuilds": {},
}

def _load_local_settings() -> dict:
    """Resolve machine-specific paths from local_settings.json + env vars + defaults."""
    settings = dict(_BUILT_IN_DEFAULTS)
    settings_path = Path(__file__).resolve().parent / "local_settings.json"
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            file_settings = json.load(f)
        for k in _BUILT_IN_DEFAULTS:
            if k in file_settings:
                settings[k] = file_settings[k]
    for k in _BUILT_IN_DEFAULTS:
        if k == "LocalBuilds":
            continue  # dict-valued, not env-overridable
        env_value = os.environ.get(k)
        if env_value:
            settings[k] = env_value
    return settings

def _read_local_geodms_version(repo_root:Path) -> str:
    """Parse rtc/dll/src/RtcGeneratedVersion.h to get '<MAJOR>.<MINOR>.<PATCH>'."""
    header = repo_root / "rtc" / "dll" / "src" / "RtcGeneratedVersion.h"
    major = minor = patch = "0"
    if header.exists():
        with open(header, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#define DMS_VERSION_MAJOR"):
                    major = line.split()[-1]
                elif line.startswith("#define DMS_VERSION_MINOR"):
                    minor = line.split()[-1]
                elif line.startswith("#define DMS_VERSION_PATCH"):
                    patch = line.split()[-1]
    return f"{major}.{minor}.{patch}"

def _resolve_local_build(version:str, settings:dict):
    """Map -version local[-flavor] to a build descriptor.
    Returns None if `version` is not a local pseudo-version.
    Returned dict: {BinDir, Suffix, RunPrefix, ExeSuffix, Flavor}.
    """
    if version == "local":
        flavor = "cmake-release"
    elif version.startswith("local-"):
        flavor = version[len("local-"):]
    else:
        return None

    repo_root = Path(settings["ProfilerDir"]).parent.as_posix()
    win_repo_tail = repo_root[2:] if len(repo_root) > 2 and repo_root[1] == ":" else repo_root
    built_in = {
        "cmake-release":   {"BinDir": f"{repo_root}/build/windows-x64-release/bin", "Suffix": "c"},
        "cmake-debug":     {"BinDir": f"{repo_root}/build/windows-x64-debug/bin",   "Suffix": "c"},
        "msbuild-release": {"BinDir": f"{repo_root}/bin/Release/x64",               "Suffix": "m"},
        "msbuild-debug":   {"BinDir": f"{repo_root}/bin/Debug/x64",                 "Suffix": "m"},
        "linux-release":   {"BinDir": f"/mnt/c{win_repo_tail}/build/linux-x64-release/bin",
                            "Suffix": "l", "RunPrefix": "wsl --", "ExeSuffix": ""},
        "linux-debug":     {"BinDir": f"/mnt/c{win_repo_tail}/build/linux-x64-debug/bin",
                            "Suffix": "l", "RunPrefix": "wsl --", "ExeSuffix": ""},
    }

    spec = dict(built_in.get(flavor, {}))
    file_builds = settings.get("LocalBuilds") or {}
    spec.update(file_builds.get(flavor, {}))

    if not spec.get("BinDir") and flavor == "cmake-release" and settings.get("LocalBuildDir"):
        spec["BinDir"] = settings["LocalBuildDir"]

    if not spec.get("BinDir"):
        raise ValueError(f"No BinDir configured for local build flavor '{flavor}'. Add LocalBuilds.{flavor}.BinDir to local_settings.json.")

    spec.setdefault("Suffix", "")
    spec.setdefault("RunPrefix", "")
    spec.setdefault("ExeSuffix", ".exe")
    spec["Flavor"] = flavor
    return spec

def get_local_machine_parameters() -> dict:
    s = _load_local_settings()
    local_machine_parameters = {}
    local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"] = s["RegressionTestsSourceDataDir"]
    local_machine_parameters["RegressionTestsAltSourceDataDir"] = s["RegressionTestsAltSourceDataDir"]
    local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"] = s["LocalDataDir"]

    # SourceDataDir mirrors the value the Windows registry holds (set via
    # GUI Options). On Linux there is no registry, so we forward it via the
    # GEODMS_directories_SourceDataDir env var. Falls back to stripping the
    # trailing /RegressionTests off RegressionTestsSourceDataDir, which is
    # how the cfg-side fallback (`%sourcedataDir%\RegressionTests`) reverses
    # the relation.
    src = s.get("SourceDataDir") or ""
    if not src:
        rts = s["RegressionTestsSourceDataDir"].rstrip("/")
        src = rts[:-len("/RegressionTests")] if rts.lower().endswith("/regressiontests") else rts
    local_machine_parameters["GEODMS_directories_SourceDataDir"] = src

    # derived
    local_machine_parameters["LocalDataDirRegression"] = f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/regression"
    local_machine_parameters["tmpFileDir"] = f"{local_machine_parameters["LocalDataDirRegression"]}/log"
    # Pass through additional roots used by get_geodms_paths.
    local_machine_parameters["ProfilerDir"] = s["ProfilerDir"]
    local_machine_parameters["LocalBuildDir"] = s["LocalBuildDir"]
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
    regression_test_paths["RSopen_RegressieTestPath_v2025"] = f"{regression_test_paths["prj_snapshotsDir"]}/RSopen_RegressieTest_v2025H2_wLB/cfg"
    regression_test_paths["CusaRunPath"] = f"{regression_test_paths["prj_snapshotsDir"]}/geodms_africa_cusa2/cfg/africa.dms"
    regression_test_paths["Networkmodel_pbl_regressietest"] = f"{regression_test_paths["prj_snapshotsDir"]}/NetworkModel_PBL_RegressieTest/cfg"
    regression_test_paths["Networkmodel_eu_regressietest"] = f"{regression_test_paths["prj_snapshotsDir"]}/networkmodel_eu_regressieTest/cfg"
    #regression_test_paths["GEODMS_Overridable_RslDataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSL"
    regression_test_paths["GEODMS_Overridable_HestiaDataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/SD51"
    regression_test_paths["GEODMS_Overridable_RSo_DataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSOpen" 
    regression_test_paths["GEODMS_Overridable_RVF_DataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RS_Landbouw" 
    regression_test_paths["GEODMS_Overridable_RSo_PrivDataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSOpen_Priv" 
    #regression_test_paths["GEODMS_Overridable_PrivDataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSOpen_Priv" 
    regression_test_paths["GEODMS_Overridable_ToBURPDataDir"]         = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/2BURP"
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = local_machine_parameters["LocalDataDirRegression"]
    regression_test_paths["GEODMS_Overridable_MondiaalDataDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/2UP"
    regression_test_paths["GEODMS_Overridable_NetworkModel_Dir"]      = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/NetworkModel_regressietest"
    regression_test_paths["GEODMS_Overridable_NetworkModelDataDir"]   = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/NetworkModel_EU_RegressionTest"
    return regression_test_paths

def get_experiments(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str) -> list:
    exps = []
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    result_folder_name = regression.get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)

    # add experiments
    regression.add_exp(exps, name=f"{result_folder_name}__t010_operator_test", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t010_operator_test.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} results/regression/t010_operator_test/stored_result", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t010_operator_test.txt", indicator_results_file=f"{result_paths["results_folder"]}/t010_operator_test.txt")
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Storage"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t050_Storage_Write_Shape_Polygon_Folder_Compare", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["StoragePath"]} EsriShape/polygon/Write", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt", file_comparison=(f"{regression_test_paths["TstDir"]}/Storage/data/polygon/area.*", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/Storage/polygon/area.*"))

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/BAG20"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["BAG20MakeSnapShotPath"]} snapshot_date_nl_geoparaat_gpkg/result_gpkg/make_geopackage", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt", file_comparison=(f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/BAG20/snapshot_Utrecht_20210701.gpkg", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/BAG20/snapshot_Utrecht_20210701.gpkg"))
    regression.add_exp(exps, name=f"{result_folder_name}__t100_network_connect", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t100_network_connect.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t100_network_connect/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t100_network_connect.txt", indicator_results_file=f"{result_paths["results_folder"]}/t100_network_connect.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t101_network_od_pc4_dense", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t101_network_od_pc4_dense.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t101_network_od_pc4_dense/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t101_network_od_pc4_dense.txt", indicator_results_file=f"{result_paths["results_folder"]}/t101_network_od_pc4_dense.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t102_network_od_pc6_sparse", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t102_network_od_pc6_sparse.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t102_network_od_pc6_sparse/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t102_network_od_pc6_sparse.txt", indicator_results_file=f"{result_paths["results_folder"]}/t102_network_od_pc6_sparse.txt") 
    regression.add_exp(exps, name=f"{result_folder_name}__t151_conversie_bl_rd_test", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t151_conversie_bl_rd_test.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["BLRDConversiePath"]} t151_conversie_bl_rd_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t151_conversie_bl_rd_test.txt", indicator_results_file=f"{result_paths["results_folder"]}/t151_conversie_bl_rd_test.txt") 
    regression.add_exp(exps, name=f"{result_folder_name}__t200_grid_Poly2Grid", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t200_grid_Poly2Grid.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t200_grid_Poly2Grid/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t200_grid_Poly2Grid.txt", indicator_results_file=f"{result_paths["results_folder"]}/t200_grid_Poly2Grid.txt") 

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t300_xml_ReadParse", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t300_xml_ReadParse.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t300_xml_ReadParse/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t300_xml_ReadParse.txt", indicator_results_file=f"{result_paths["results_folder"]}/t300_xml_ReadParse.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t301_BAG_ResidentialType", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t301_BAG_ResidentialType.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t301_BAG_ResidentialType/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t301_BAG_ResidentialType.txt", indicator_results_file=f"{result_paths["results_folder"]}/t301_BAG_ResidentialType.txt") 

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/NetworkModel"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t405_1_NetworkModel_PBL_prepare_data", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_1_NetworkModel_PBL_prepare_data.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step1_prepare_data", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_1_NetworkModel_PBL_prepare_data.txt")

    regression_test_paths["UseFence"] = "FALSE"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t405_2_NetworkModel_PBL_zonderFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_2_NetworkModel_PBL_zonderFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step2_1_run_model_tiled_zonderFence", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_2_NetworkModel_PBL_zonderFence.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t405_2_2_NetworkModel_PBL_indicator_zonderFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_2_2_NetworkModel_PBL_indicator_zonderFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/t405_2_NetworkModel_PBL_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_2_2_NetworkModel_PBL_indicator_zonderFence.txt", store_results=False)
    
    regression_test_paths["UseFence"] = "TRUE"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t405_3_NetworkModel_PBL_metFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_3_NetworkModel_PBL_metFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step2_2_run_model_tiled_metFence", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_3_NetworkModel_PBL_metFence.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t405_3_2_NetworkModel_PBL_indicator_metFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_3_2_NetworkModel_PBL_indicator_metFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/t405_3_NetworkModel_PBL_fenced_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_3_2_NetworkModel_PBL_indicator_metFence.txt", store_results=False)

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/networkmodel_eu_regressietest"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t410_NetworkModel_EU", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t410_NetworkModel_EU.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_eu_regressietest"]}/main.dms RegressieTest/t410_NetworkModel_EU_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t410_NetworkModel_EU.txt")

    #regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Hestia"
    #env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    #add_exp(exps, name=f"{result_folder_name}__t530_Hestia_2024", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t530_hestia2024.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["HestiaRunPath"]} t530_hestia2024/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t530_hestia2024.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/LUSDemo2023"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t611_Lus_demo_2023", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t611_Lus_demo_2023.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["LusDemoRunPath2023"]} t611_lus_demo_2023_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t611_Lus_demo_2023.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/RSopen_RegressieTest_v2025"
    regression_test_paths["AlleenEindjaar"] = "FALSE"
    #regression_test_paths["VariantDataOntkoppeld"] = "TRUE"
    #env_vars = get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    #add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_indicator_results_test_Generate", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_Generate.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath"]}/Regression_test.dms Analysis/Allocatie/Zichtjaren/Y2050/Impl/Generate", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_Generate.txt")
    #add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_indicator_results_test_result_html", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_result_html.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath"]}/Regression_test.dms t640_3_RSopen_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_results_test_result_html.txt")
    regression_test_paths["VariantDataOntkoppeld"] = "FALSE"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t641_1_RSopen_MakeBaseData", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_1_RSopen_MakeBaseData.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms WriteBasedata/Generate_Run1", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_1_RSopen_MakeBaseData.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t641_1_2_RSopen_prepare_base_data_indicator", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_1_2_RSopen_prepare_base_data_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms /t641_1_RSopen_MakeBaseData/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_1_2_RSopen_prepare_base_data_indicator.txt", store_results=False)
    
    regression_test_paths["VariantDataOntkoppeld"] = "FALSE"
    regression_test_paths["IsProductieRun"] = "FALSE"
    regression_test_paths["RSL_VARIANT_NAME"] = "BAU"
    regression_test_paths["AlleenEindjaar"] = "FALSE"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t641_2_RSopen_MakeVariantData", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms WriteVariantData/Generate_Run1", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t641_2_RSopen_MakeVariantData_indicator", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms t641_2_RSopen_MakeVariantData/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_2_RSopen_MakeVariantData_indicator.txt", store_results=False)

    regression_test_paths["VariantDataOntkoppeld"] = "TRUE"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_Allocatie", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_Allocatie.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms Allocatie/Zichtjaren/Y2050/Impl/Generate", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_Allocatie.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_indicator_indicator",  cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms t641_3_RSopen_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_indicator.txt", store_results=False)

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/2UP"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t710_2UP", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t710_2UP.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["TwoUPRunPath"]} test_2UP_indicator_results/result_html_zonder_calcache", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t710_2UP.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/2BURP"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t720_2BURP", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t720_2BURP.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["TwoBURPRunPath"]} t720_2BURP_indicator_results/result", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t720_2BURP.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/100m_DynaPop"
    regression_test_paths["GEODMS_Overridable_SourceDataProjDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}"
    #regression_test_paths["GEODMS_Overridable_RunRegions"] = "JrcRegion"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t810_ValLuisa", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t810_ValLuisa.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["DynaPopPath"]} t810_ValLuisa_Czech_LU_POP/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t810_ValLuisa.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Cusa"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    regression.add_exp(exps, name=f"{result_folder_name}__t910_Cusa2_Africa", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t910_Cusa2_Africa.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["CusaRunPath"]} t910_cusa2_Africa_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t910_Cusa2_Africa.txt")


    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/gui"
    regression.add_exp(exps, name=f"{result_folder_name}__t1630_expandtest", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1630_expandtest.txt /T{regression_test_paths["TstDir"]}/dmsscript/RSLight_2020_expand_S1S2.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["RSLight_2020Path"]} t1630_expandtest_S1S2", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1630_expandtest.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t1640_value_info", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1640_value_info.txt /T{regression_test_paths["TstDir"]}/dmsscript/value_info.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} t1640_value_info", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1640_value_info.txt")
    regression.add_exp(exps, name=f"{result_folder_name}__t1642_value_info_group_by", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1642_value_info_group_by.txt /T{regression_test_paths["TstDir"]}/dmsscript/value_info_group_by.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["TstDir"]}/operator/cfg/MicroTst.dms t1642_value_info_group_by", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1642_value_info_group_by.txt")

    generated_statfile = f"{local_machine_parameters["tmpFileDir"]}/t1742_command_statistics_stat.html"
    reference_statfile = f"{regression_test_paths["TstDir"]}/norm/Statistics_AUAA.html"
    regression.add_exp(exps, name=f"{result_folder_name}__t1742_command_statistics", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t1742_command_statistics.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} @statistics /Arithmetics/UnTiled/add/attr @file {generated_statfile}", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1742_command_statistics.txt", file_comparison=(reference_statfile, generated_statfile))
    return exps

def remove_local_data_dir_regression(local_data_regression_folder:str):
    files = glob.glob(local_data_regression_folder+"/*")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        else:
            shutil.rmtree(f)
    return

# Workaround for https://github.com/ObjectVision/GeoDMS/issues/1101 — the
# 20.0.0 GeoDMS binary cannot overwrite existing .dmsdata files whose names
# contain non-ASCII characters (e.g. `_β`). Wipe the known-affected .fss
# folders before each run so each test starts with fresh-create semantics.
_ISSUE_1101_AFFECTED_FSS = [
    "RSopen_RegressieTest_v2025/BaseData/Vastgoed/Verblijfsrecreatie/Provincie/Betas_Objecten_Nederland.fss",
]

def workaround_issue_1101(local_data_dir_regression:str):
    for rel in _ISSUE_1101_AFFECTED_FSS:
        path = f"{local_data_dir_regression}/{rel}"
        if not os.path.isdir(path):
            continue
        for f in glob.glob(f"{path}/*"):
            try:
                os.remove(f) if os.path.isfile(f) else shutil.rmtree(f)
            except OSError as e:
                print(f"[1101 workaround] could not remove {f}: {e}")
        print(f"[1101 workaround] cleaned: {path}")
    return

_FLAVOR_RE = re.compile(r'^(\d+(?:\.\d+)+)([a-z])$')

# Windows absolute paths anywhere in a string. The "preceded by" alternation
# avoids URL false positives (`https://` — where `s` is part of a multi-letter
# scheme name) while still matching switch-attached paths (`/LC:/foo` — where
# `C` is preceded by `/L`, i.e. a slash + a single switch-letter). Drive
# letters used in actual cmds are always exactly one letter.
_WIN_PATH_RE = re.compile(r"(^|[\s;=\"']|/[A-Za-z])([A-Za-z]):[/\\]([^\s;\"']*)")

def to_wsl_path(s:str) -> str:
    """Translate every Windows absolute path in `s` to its WSL `/mnt/<letter>/…`
    equivalent. Non-path tokens, env-var names, switches like `/S1`, and the
    `wsl --` prefix all pass through unchanged.

    Examples:
        "C:/dev/tst"                          -> "/mnt/c/dev/tst"
        "F:\\\\SourceData\\\\BAG20"           -> "/mnt/f/SourceData/BAG20"
        "wsl -- /opt/.../GeoDmsRun /LC:/log.txt /S1 C:/cfg/x.dms target"
            -> "wsl -- /opt/.../GeoDmsRun /L/mnt/c/log.txt /S1 /mnt/c/cfg/x.dms target"
        "https://example.com/page"            -> unchanged (URL scheme not a drive)
    """
    def repl(m):
        prefix = m.group(1) or ''
        letter = m.group(2).lower()
        rest = m.group(3).replace(chr(92), '/')
        return f"{prefix}/mnt/{letter}/{rest}"
    return _WIN_PATH_RE.sub(repl, s)

def _display_version_with_flavor_dot(version:str) -> str:
    """Make sure the display-version inserts a dot before any one-letter
    flavor suffix (m / c / l / …) so the folder name later splits cleanly
    on `_` into [major, minor, patch, flavor, arch, …].

    `20.0.0c` -> `20.0.0.c`     # split-on-`_` gives [20, 0, 0, c, …]
    `20.0.0`  -> `20.0.0`       # no flavor letter, unchanged
    `local`   -> `local`        # not numeric, unchanged

    Without this, `20.0.0c` produces folder `20_0_0c_x64_…` which
    `parse_folder_name` reads as patch=`0c`, no flavor, breaking the
    report's column lookup for that run.
    """
    m = _FLAVOR_RE.match(version)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    return version

def get_geodms_paths(version:str) -> dict:
    assert(version)
    s = _load_local_settings()
    geodms_paths = {}
    geodms_paths["GeoDmsPlatform"] = "x64"
    # version="local" / "local-<flavor>" resolves to a working-copy build via
    # LocalBuilds (see _resolve_local_build). Any other value resolves to an
    # installed GeoDms{version} under %ProgramFiles%/ObjectVision/.
    local_spec = _resolve_local_build(version, s)
    if local_spec is not None:
        geodms_paths["GeoDmsPath"] = f"\"{local_spec["BinDir"]}\""
        numeric_version = _read_local_geodms_version(Path(s["ProfilerDir"]).parent)
        suffix = local_spec["Suffix"]
        geodms_paths["GeoDmsDisplayVersion"] = f"{numeric_version}.{suffix}" if suffix else numeric_version
        geodms_paths["GeoDmsRunPrefix"] = local_spec["RunPrefix"]
        geodms_paths["GeoDmsExeSuffix"] = local_spec["ExeSuffix"]
        geodms_paths["GeoDmsLocalFlavor"] = local_spec["Flavor"]
    else:
        # Canonicalise the user-supplied version to the dotted form the
        # rest of the pipeline expects (folder name parser splits on `_`
        # into [major, minor, patch, flavor, arch, …], install dirs are
        # named GeoDms<ver>.<flavor>, etc.). Accepts either form on the
        # CLI: `-version 20.0.0.l` (canonical) or `-version 20.0.0l`
        # (compact, kept as a courtesy).
        canonical = _display_version_with_flavor_dot(version)
        if canonical.endswith(".l"):
            # Linux flavor installed via .deb (nsi/CreateLinuxSetup.sh) at
            # /opt/ObjectVision/GeoDms<canonical>. Invoked via `wsl --` so
            # the rest of the test command (paths, env vars, args) is
            # forwarded into the WSL distro.
            geodms_paths["GeoDmsPath"] = f"/opt/ObjectVision/GeoDms{canonical}"
            geodms_paths["GeoDmsDisplayVersion"] = canonical
            geodms_paths["GeoDmsRunPrefix"] = "wsl --"
            geodms_paths["GeoDmsExeSuffix"] = ""
            geodms_paths["GeoDmsLocalFlavor"] = "linux-release"
        else:
            geodms_paths["GeoDmsPath"] = f"\"{os.path.expandvars(f"%ProgramFiles%/ObjectVision/GeoDms{canonical}")}\""
            geodms_paths["GeoDmsDisplayVersion"] = canonical
            geodms_paths["GeoDmsRunPrefix"] = ""
            geodms_paths["GeoDmsExeSuffix"] = ".exe"
            geodms_paths["GeoDmsLocalFlavor"] = ""
    geodms_paths["GeoDmsProfilerPath"] = f"{s["ProfilerDir"]}/profiler.py"
    geodms_paths["GeoDmsRegressionPath"] = f"{s["ProfilerDir"]}/regression.py"
    exe = geodms_paths["GeoDmsExeSuffix"]
    # If a RunPrefix is set (e.g. "wsl --" for linux-release flavors), prepend
    # it so any consumer that just builds f"{GeoDmsRunPath} <args>" actually
    # invokes the binary through WSL rather than as a direct Windows process.
    prefix = geodms_paths["GeoDmsRunPrefix"]
    prefix_str = f"{prefix} " if prefix else ""
    geodms_paths["GeoDmsRunPath"] = f"{prefix_str}{geodms_paths["GeoDmsPath"]}/GeoDmsRun{exe}"
    geodms_paths["GeoDmsGuiQtPath"] = f"{prefix_str}{geodms_paths["GeoDmsPath"]}/GeoDmsGuiQt{exe}"
    return geodms_paths

def run_full_regression_test(version:str="18.0.3", MT1="S1", MT2="S2", MT3="S3"):
    parser = argparse.ArgumentParser()
    parser.add_argument("-version", help="Geodms version ie: 17.4.6")
    parser.add_argument("-MT1", help="Multithreading 1: S1 or C1")
    parser.add_argument("-MT2", help="Multithreading 2: S2 or C2")
    parser.add_argument("-MT3", help="Multithreading 3: S3 or C3")
    parser.add_argument(
        "-tests",
        help=(
            "Comma-separated test-name substrings to run. Substring is matched "
            "against the full experiment name. Examples: '-tests t060' runs only "
            "the t060_ test; '-tests t060,t301' runs both; '-tests t06' runs all "
            "t06* (t060, t061, ...). Omit to run the full suite."
        ),
    )
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
    import_module_from_path(geodms_paths["GeoDmsRegressionPath"])
    regression.import_module_from_path(geodms_paths["GeoDmsProfilerPath"])
    
    geodms_paths["GeoDmsProfilerPath"] = f'C:/Users/Cicada/dev/geodms/branches/geodms_v18/profiler/profiler.py'
    geodms_paths["GeoDmsProfilerPath"] = f'C:/Users/Cicada/dev/geodms/branches/geodms_v18/profiler/profiler.py'

    display_version = geodms_paths["GeoDmsDisplayVersion"]
    regression_test_paths = get_regression_test_paths(local_machine_parameters)
    result_paths = regression.get_result_paths(geodms_paths, regression_test_paths, display_version, MT1, MT2, MT3)
    #remove_local_data_dir_regression(local_machine_parameters["LocalDataDirRegression"])
    #import_module_from_path(geodms_paths["GeoDmsProfilerPath"])

    regression.header_stuff_to_be_removed_in_future(local_machine_parameters, result_paths, MT1, MT2, MT3)
    workaround_issue_1101(local_machine_parameters["LocalDataDirRegression"])
    operator_experiments = get_experiments(local_machine_parameters, geodms_paths, regression_test_paths, result_paths, display_version, MT1, MT2, MT3)

    # Linux-flavor path translation. The whole command line + every env var
    # value contains Windows-style paths (C:/…, F:/…); the WSL-side binary
    # needs them in /mnt/<letter>/… form. Translate both, and prepend a
    # `WSLENV=…` entry so wsl.exe forwards the (now POSIX-shaped) values
    # to the Linux distro. Without this every linux-flavor test fails
    # at the first I/O on the cfg path or log path.
    if geodms_paths.get("GeoDmsLocalFlavor") == "linux-release":
        for exp in operator_experiments:
            exp.command = to_wsl_path(exp.command)
            if exp.environment_variables:
                ev = to_wsl_path(exp.environment_variables)
                # Build WSLENV listing every variable name so wsl.exe propagates
                # them (without /p — we've already translated paths ourselves).
                names = [pair.split('=', 1)[0].strip()
                         for pair in ev.split(';') if '=' in pair]
                ev = ev + ';WSLENV=' + ':'.join(names)
                exp.environment_variables = ev

        # Override results_folder.txt with the WSL-translated path so the
        # cfg-side `results_folder` parameter (read via %LocalDataDir%/.../
        # results_folder.txt) hands the Linux binary a /mnt/c/… path instead
        # of a C:/… path that maps to nowhere on Linux.
        rf_path = f"{local_machine_parameters['tmpFileDir']}/results_folder.txt"
        with open(rf_path, "w") as f:
            f.write(to_wsl_path(result_paths["results_folder"]))

    # Optional test-name filter for fast iteration. The HTML report still
    # picks up cached results for the unselected tests, so consistency with
    # a full prior run is preserved — only the listed tests are re-executed.
    # We also wipe the matching .bin caches so the runner actually re-runs
    # the targeted tests (otherwise it skips them with "results are reused").
    if args.tests:
        filters = [t.strip() for t in args.tests.split(",") if t.strip()]
        filtered = [exp for exp in operator_experiments
                    if any(f in exp.name for f in filters)]
        if not filtered:
            print(f"-tests filter {filters} matched 0 experiments out of "
                  f"{len(operator_experiments)}; available names:", file=sys.stderr)
            for exp in operator_experiments:
                print(f"  {exp.name}", file=sys.stderr)
            sys.exit(2)
        print(f"-tests filter {filters} -> running {len(filtered)} of "
              f"{len(operator_experiments)} experiments:")
        wiped = 0
        for exp in filtered:
            print(f"  {exp.name}")
            cache = f"{result_paths['results_folder']}/{exp.name}.bin"
            if os.path.exists(cache):
                os.remove(cache)
                wiped += 1
        if wiped:
            print(f"-tests: wiped {wiped} cached .bin file(s) to force re-run")
        operator_experiments = filtered

    regression.run_experiments(operator_experiments)
    regression.collect_and_generate_test_results(display_version, result_paths)

    return

if __name__=="__main__":
    run_full_regression_test()