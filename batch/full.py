# Before running tests, read the operational wiki -- it captures the non-obvious
# gotchas (detaching runs, WSL/Linux, references, the report, integrity rules):
#   https://github.com/ObjectVision/GeoDMS-Test/wiki/Running-tests-with-Claude
#   https://github.com/ObjectVision/GeoDMS-Test/wiki/Running-Linux-tests-on-Windows
#   https://github.com/ObjectVision/GeoDMS-Test/wiki/Test-references-and-report-generation
#
# Long runs: do NOT launch this as a child of an interactive terminal or an
# automation/agent session -- such a child gets killed when that session is
# cleaned up (the whole python + wsl-bridge + GeoDmsRun tree dies at once, no
# error, GeoDMS log cut off mid-line; looks like a crash but is not). Use the
# detached launcher instead:  batch\run_detached.ps1 -Version <ver> [-Tests ...]
# It starts the run as a session-independent Windows process (Start-Process),
# logs stdout/stderr to a file, and saves the PID next to the results.
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
import subprocess

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
    # Where result folders + the HTML report are stored. Keep this OUT of the
    # per-user working copy so several working copies / users share one result
    # history. If blank, falls back to <TstDir>/Regression/GeoDMSTestResults.
    "ResultsBaseDir": "C:/LocalData/GeoDMS-Test/Regression",
    # ProfilerDir is ONLY used for `-version local` builds: its parent is taken
    # as the GeoDMS source-repo root (to read the build version + locate bin/).
    # The report scripts no longer come from here (see report_scripts_dir below).
    # A test machine that only tests installed GeoDms versions can ignore this.
    "ProfilerDir": "C:/dev/GeoDMS/profiler",
    "LocalBuildDir": str(Path(__file__).resolve().parent.parent.parent / "GeoDMS" / "build" / "windows-x64-release" / "bin").replace("\\", "/"),
    "LocalBuilds": {},
    # Limit the HTML/bokeh report columns to full GitHub releases (no
    # pre-releases or drafts) plus the version under test. Set to false to
    # compare against every historical result folder again.
    "ReportOnlyReleases": True,
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
    local_machine_parameters["RegressionTestsSourceDataDir"] = s["RegressionTestsSourceDataDir"]
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
    regression_test_paths["BatchDir"] = str(os.getcwd()).replace("\\", "/")
    regression_test_paths["TstDir"] = str(Path(regression_test_paths["BatchDir"]).parent.absolute()).replace("\\", "/")
    # Projectconfiguraties zijn gemigreerd van %RegressionTestsSourceDataDir%/prj_snapshots
    # naar de repo zelf (GeoDMS-Test/projects) zodat ze onder versiebeheer staan;
    # de bijbehorende (grote) data staat in SourceData en wordt via
    # GEODMS_Overridable_*-env-vars aan de configs doorgegeven.
    regression_test_paths["projectsDir"] = f"{regression_test_paths["TstDir"]}/Projects"

    regression_test_paths["OperatorPath"] = f"{regression_test_paths["TstDir"]}/Operator/cfg/Operator.dms"
    regression_test_paths["StoragePath"] = f"{regression_test_paths["TstDir"]}/Storage/cfg/Regression.dms"
    regression_test_paths["StorageGDALPath"] = f"{regression_test_paths["TstDir"]}/Storage_gdal/cfg/Regression.dms"
    regression_test_paths["RegressionPath"] = f"{regression_test_paths["TstDir"]}/Regression/cfg/stam.dms"
    regression_test_paths["BLRDConversiePath"] = f"{regression_test_paths["projectsDir"]}/bl_rd_conversie/cfg/root.dms"

    regression_test_paths["LusDemoRunPath2023"] = f"{regression_test_paths["projectsDir"]}/lus_demo_2023/cfg/demo.dms"
    regression_test_paths["RSLight_2020Path"] = f"{regression_test_paths["projectsDir"]}/RSLight_2020/cfg/Regression_test.dms"
    regression_test_paths["HestiaDevelopment"] = f"{regression_test_paths["projectsDir"]}/model-hestia-development.main_18_0_4/Runs/HestiaRun.dms"

    regression_test_paths["TwoUPRunPath"] = f"{regression_test_paths["projectsDir"]}/2UP/cfg/stam.dms"
    regression_test_paths["TwoBURPRunPath"] = f"{regression_test_paths["projectsDir"]}/2BURP/cfg/main.dms"
    regression_test_paths["DynaPopPath"] = f"{regression_test_paths["projectsDir"]}/100m_DynaPop/cfg/StatusQuo.dms"
    regression_test_paths["BAG20MakeSnapShotPath"] = f"{regression_test_paths["projectsDir"]}/BAG20/cfg/BAG20_MakeSnaphot.dms"
    regression_test_paths["RSopen_RegressieTestPath_v2025"] = f"{regression_test_paths["projectsDir"]}/RSopen_RegressieTest_v2025H2_wLB/cfg"
    regression_test_paths["CusaRunPath"] = f"{regression_test_paths["projectsDir"]}/geodms_africa_cusa2/cfg/africa.dms"
    regression_test_paths["Networkmodel_pbl_regressietest"] = f"{regression_test_paths["projectsDir"]}/NetworkModel_PBL_RegressieTest/cfg"
    regression_test_paths["Networkmodel_eu_regressietest"] = f"{regression_test_paths["projectsDir"]}/NetworkModel_EU_regressietest/cfg"
    regression_test_paths["GEODMS_Overridable_HestiaDataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/SD51"
    regression_test_paths["GEODMS_Overridable_RSo_DataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSOpen"
    # Env-namen moeten exact matchen met de parameternamen in ConfigSettings/Overridable
    # van de RSopen-config (RS_Lb_DataDir, PrivDataDir) — anders valt GeoDMS terug op
    # registry-overrides (HKCU\Software\ObjectVision\<machine>\GeoDMS) of de config-default.
    regression_test_paths["GEODMS_Overridable_RS_Lb_DataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RS_Landbouw"
    regression_test_paths["GEODMS_Overridable_PrivDataDir"] = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/RSOpen_Priv"
    regression_test_paths["GEODMS_Overridable_ToBURPDataDir"]         = f"{local_machine_parameters["RegressionTestsAltSourceDataDir"]}/2BURP"
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = local_machine_parameters["LocalDataDirRegression"]
    regression_test_paths["GEODMS_Overridable_MondiaalDataDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/2UP"
    regression_test_paths["GEODMS_Overridable_CUSA2_DataDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/CUSA2"
    regression_test_paths["GEODMS_Overridable_LUSDemo_DataDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/LUS_Demo"
    regression_test_paths["GEODMS_Overridable_NetworkModel_Dir"]      = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/NetworkModel_PBL"
    regression_test_paths["GEODMS_Overridable_NetworkModelDataDir"]   = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/NetworkModel_EU"
    # Centrale map met referentie-/benchmark-bestanden, per test in een submap.
    # Configs lezen deze via %TestRefDir%; full.py-file_comparisons via onderstaande paden.
    regression_test_paths["TestRefDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}/TestReferenceFiles"
    regression_test_paths["GEODMS_Overridable_TestRefDir"] = regression_test_paths["TestRefDir"]
    return regression_test_paths

def get_experiments(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict, version:str, MT1:str, MT2:str, MT3:str) -> list:
    exps = []
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    result_folder_name = regression.get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)

    # add experiments
    # t010 — Operator/functie-test: draait de Operator-config die vele DMS-operatoren/functies dekt.
    regression.add_exp(exps, name=f"{result_folder_name}__t010_operator_test", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t010_operator_test.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} results/regression/t010_operator_test/stored_result", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t010_operator_test.txt", indicator_results_file=f"{result_paths["results_folder"]}/t010_operator_test.txt")
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Storage"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t050 — Storage: schrijf ESRI-shapefile (polygon) via de storage manager; round-trip-test.
    #        De referentie is tevens de bron-input (Storage/data/polygon/area.*) en blijft daarom
    #        bij de config in de repo — niet in TestReferenceFiles.
    regression.add_exp(exps, name=f"{result_folder_name}__t050_Storage_Write_Shape_Polygon_Folder_Compare", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["StoragePath"]} EsriShape/polygon/Write", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t050_Storage_Write_Shape_Polygon_Folder_Compare.txt", file_comparison=(f"{regression_test_paths["TstDir"]}/Storage/data/polygon/area.*", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/Storage/polygon/area.*"))

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/BAG20"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t060 — Storage: maak BAG-snapshot Utrecht in GeoPackage-formaat; vergelijk gegenereerde .gpkg met referentie.
    regression.add_exp(exps, name=f"{result_folder_name}__t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["BAG20MakeSnapShotPath"]} snapshot_date_nl_geoparaat_gpkg/result_gpkg/make_geopackage", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t060_Storage_BAGSnapshot_Utrecht_GeoPackage_Compare.txt", file_comparison=(f"{regression_test_paths["TestRefDir"]}/t060/snapshot_Utrecht_20210701.gpkg", f"{local_machine_parameters["GEODMS_DIRECTORIES_LOCALDATADIR"]}/Regression/BAG20/snapshot_Utrecht_20210701.gpkg"))
    # t100 — Netwerk: verbind PC6-punten aan het wegennet (NL/BE/GE); vergelijk met opgenomen referentie.
    regression.add_exp(exps, name=f"{result_folder_name}__t100_network_connect", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t100_network_connect.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t100_network_connect/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t100_network_connect.txt", indicator_results_file=f"{result_paths["results_folder"]}/t100_network_connect.txt")
    # t101 — Netwerk: OD PC4 dense impedance-matrix over wegennet (NL/BE/GE). (Mantis #1021, gearchiveerd)
    regression.add_exp(exps, name=f"{result_folder_name}__t101_network_od_pc4_dense", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t101_network_od_pc4_dense.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t101_network_od_pc4_dense/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t101_network_od_pc4_dense.txt", indicator_results_file=f"{result_paths["results_folder"]}/t101_network_od_pc4_dense.txt")
    # t102 — Netwerk: OD PC6 sparse impedance-matrix (met cut) over wegennet (NL/BE/GE). (Mantis #1021, gearchiveerd)
    regression.add_exp(exps, name=f"{result_folder_name}__t102_network_od_pc6_sparse", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t102_network_od_pc6_sparse.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t102_network_od_pc6_sparse/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t102_network_od_pc6_sparse.txt", indicator_results_file=f"{result_paths["results_folder"]}/t102_network_od_pc6_sparse.txt") 
    # t151 — Conversie van Belgische (Lambert) naar RD-coördinaten voor Belgische gemeenten.
    regression.add_exp(exps, name=f"{result_folder_name}__t151_conversie_bl_rd_test", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t151_conversie_bl_rd_test.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["BLRDConversiePath"]} t151_conversie_bl_rd_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t151_conversie_bl_rd_test.txt", indicator_results_file=f"{result_paths["results_folder"]}/t151_conversie_bl_rd_test.txt") 
    # t200 — Grid: poly2grid van CBS-bodemgebruik (BBG) naar 10m-grid (NL). (Mantis #929, gearchiveerd)
    regression.add_exp(exps, name=f"{result_folder_name}__t200_grid_Poly2Grid", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t200_grid_Poly2Grid.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t200_grid_Poly2Grid/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t200_grid_Poly2Grid.txt", indicator_results_file=f"{result_paths["results_folder"]}/t200_grid_Poly2Grid.txt") 

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t300 — XML-bestanden (BAG) lezen en polygon-geometrieën parsen.
    regression.add_exp(exps, name=f"{result_folder_name}__t300_xml_ReadParse", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t300_xml_ReadParse.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t300_xml_ReadParse/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t300_xml_ReadParse.txt", indicator_results_file=f"{result_paths["results_folder"]}/t300_xml_ReadParse.txt")
    # t301 — Woningtype (residential type) afleiden uit BAG-geometrie pand/vbo; vergelijk met referentie (1 promille foutmarge).
    regression.add_exp(exps, name=f"{result_folder_name}__t301_BAG_ResidentialType", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t301_BAG_ResidentialType.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RegressionPath"]} results/t301_BAG_ResidentialType/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t301_BAG_ResidentialType.txt", indicator_results_file=f"{result_paths["results_folder"]}/t301_BAG_ResidentialType.txt")

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/NetworkModel"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t405_1 — NetworkModel PBL, stap 1: invoerdata prepareren.
    regression.add_exp(exps, name=f"{result_folder_name}__t405_1_NetworkModel_PBL_prepare_data", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_1_NetworkModel_PBL_prepare_data.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step1_prepare_data", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_1_NetworkModel_PBL_prepare_data.txt")

    regression_test_paths["UseFence"] = "FALSE"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t405_2 — NetworkModel PBL, stap 2.1: tiled modelrun zonder fence (UseFence=FALSE).
    regression.add_exp(exps, name=f"{result_folder_name}__t405_2_NetworkModel_PBL_zonderFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_2_NetworkModel_PBL_zonderFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step2_1_run_model_tiled_zonderFence", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_2_NetworkModel_PBL_zonderFence.txt")
    # t405_2_2 — indicator-vergelijking van de zonderFence-run.
    regression.add_exp(exps, name=f"{result_folder_name}__t405_2_2_NetworkModel_PBL_indicator_zonderFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_2_2_NetworkModel_PBL_indicator_zonderFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/t405_2_NetworkModel_PBL_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_2_2_NetworkModel_PBL_indicator_zonderFence.txt", store_results=False)
    
    regression_test_paths["UseFence"] = "TRUE"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t405_3 — NetworkModel PBL, stap 2.2: tiled modelrun met fence (UseFence=TRUE).
    regression.add_exp(exps, name=f"{result_folder_name}__t405_3_NetworkModel_PBL_metFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_3_NetworkModel_PBL_metFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/Step2_2_run_model_tiled_metFence", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_3_NetworkModel_PBL_metFence.txt")
    # t405_3_2 — indicator-vergelijking van de metFence-run.
    regression.add_exp(exps, name=f"{result_folder_name}__t405_3_2_NetworkModel_PBL_indicator_metFence", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t405_3_2_NetworkModel_PBL_indicator_metFence.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_pbl_regressietest"]}/main.dms RegressieTest/t405_3_NetworkModel_PBL_fenced_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t405_3_2_NetworkModel_PBL_indicator_metFence.txt", store_results=False)

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/networkmodel_eu_regressietest"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t410 — NetworkModel EU: indicator-results regressietest.
    regression.add_exp(exps, name=f"{result_folder_name}__t410_NetworkModel_EU", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t410_NetworkModel_EU.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["Networkmodel_eu_regressietest"]}/main.dms RegressieTest/t410_NetworkModel_EU_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t410_NetworkModel_EU.txt")

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/LUSDemo2023"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t611 — LUS Demo 2023 (Land Use Scanner): allocatie-resultaten vergelijken.
    regression.add_exp(exps, name=f"{result_folder_name}__t611_Lus_demo_2023", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t611_Lus_demo_2023.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["LusDemoRunPath2023"]} t611_lus_demo_2023_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t611_Lus_demo_2023.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/RSopen_RegressieTest_v2025"
    regression_test_paths["AlleenEindjaar"] = "FALSE"
    # VariantDataOntkoppeld wordt bewust NIET via een env-var gezet: de config
    # is leidend (ModelParameters/VariantDataOntkoppeld := FALSE). Daardoor
    # berekent de allocatie (t641_3) de variantdata inline en is de losse
    # WriteVariantData-stap (voorheen t641_2) overbodig. Zie issue #22.
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t641_1 — RuimteScanner Open v2025H2: basisdata genereren (WriteBasedata).
    regression.add_exp(exps, name=f"{result_folder_name}__t641_1_RSopen_MakeBaseData", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_1_RSopen_MakeBaseData.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms WriteBasedata/Generate_Run1", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_1_RSopen_MakeBaseData.txt")
    # t641_1_2 — indicator-vergelijking van de basisdata-stap.
    regression.add_exp(exps, name=f"{result_folder_name}__t641_1_2_RSopen_prepare_base_data_indicator", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_1_2_RSopen_prepare_base_data_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms /t641_1_RSopen_MakeBaseData/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_1_2_RSopen_prepare_base_data_indicator.txt", store_results=False)
    
    regression_test_paths["IsProductieRun"] = "FALSE"
    regression_test_paths["RSL_VARIANT_NAME"] = "BAU"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t641_3 — RSopen: allocatie zichtjaar Y2050. De variantdata wordt inline
    #          meeberekend (VariantDataOntkoppeld=FALSE, bepaald door de config,
    #          niet door full.py). Voorheen draaide hiervoor de losse t641_2-stap.
    regression.add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_Allocatie", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_Allocatie.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms Allocatie/Zichtjaren/Y2050/Impl/Generate", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_Allocatie.txt")
    # t641_3 (indicator) — indicator-vergelijking van de allocatie.
    regression.add_exp(exps, name=f"{result_folder_name}__t641_3_RSopen_indicator_indicator", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_indicator.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["RSopen_RegressieTestPath_v2025"]}/Regression_test.dms t641_3_RSopen_indicator_results_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t641_3_RSopen_indicator_indicator.txt", store_results=False)

    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/2UP"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t710 — 2UP-model (mondiaal urbanisatiemodel): indicator-results, zonder calcache.
    regression.add_exp(exps, name=f"{result_folder_name}__t710_2UP", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t710_2UP.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["TwoUPRunPath"]} test_2UP_indicator_results/result_html_zonder_calcache", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t710_2UP.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/2BURP"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t720 — 2BURP-model: indicator-results regressietest.
    regression.add_exp(exps, name=f"{result_folder_name}__t720_2BURP", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t720_2BURP.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["TwoBURPRunPath"]} t720_2BURP_indicator_results/result", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t720_2BURP.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/100m_DynaPop"
    regression_test_paths["GEODMS_Overridable_SourceDataProjDir"] = f"{local_machine_parameters["GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"]}"
    #regression_test_paths["GEODMS_Overridable_RunRegions"] = "JrcRegion"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t810 — ValLuisa/100m_DynaPop (EuClueScanner): LandUse & bevolking Tsjechië 2050 op 100m.
    regression.add_exp(exps, name=f"{result_folder_name}__t810_ValLuisa", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t810_ValLuisa.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["DynaPopPath"]} t810_ValLuisa_Czech_LU_POP/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t810_ValLuisa.txt")
    
    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/Cusa"
    env_vars = regression.get_full_regression_test_environment_string(local_machine_parameters, geodms_paths, regression_test_paths, result_paths)
    # t910 — Cusa2 Afrika-model (geodms_africa_cusa2): indicator-results regressietest.
    regression.add_exp(exps, name=f"{result_folder_name}__t910_Cusa2_Africa", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t910_Cusa2_Africa.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["CusaRunPath"]} t910_cusa2_Africa_test/result_html", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t910_Cusa2_Africa.txt")


    regression_test_paths["GEODMS_DIRECTORIES_LOCALDATAPROJDIR"] = f"{local_machine_parameters["LocalDataDirRegression"]}/gui"
    # t1630 — GUI-robuustheidstest: klap SourceData/Claims/ReadData van RSLight_2020 volledig
    #         uit (items worden rood door onbereikbare RSL-data — dat is verwacht) en check dat
    #         de GUI dit overleeft; het gescoorde resultaat is een classificatie-labelcheck.
    #         (Mantis #887/#1429, gearchiveerd)
    regression.add_exp(exps, name=f"{result_folder_name}__t1630_expandtest", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1630_expandtest.txt /T{regression_test_paths["TstDir"]}/dmsscript/RSLight_2020_expand_{MT1}{MT2}.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["RSLight_2020Path"]} t1630_expandtest_{MT1}{MT2}", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1630_expandtest.txt")
    # t1640 — GUI: vergelijk detailpagina value-info op aggregaties met opgenomen referentie (14.5.0). (Mantis #1434, gearchiveerd)
    regression.add_exp(exps, name=f"{result_folder_name}__t1640_value_info", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1640_value_info.txt /T{regression_test_paths["TstDir"]}/dmsscript/value_info.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} t1640_value_info", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1640_value_info.txt")
    # t1642 — GUI: vergelijk detailpagina statistics/value-info met group-by op geometrie. (Mantis #1438, gearchiveerd)
    regression.add_exp(exps, name=f"{result_folder_name}__t1642_value_info_group_by", cmd=f"{geodms_paths["GeoDmsGuiQtPath"]} /L{result_paths["results_log_folder"]}/t1642_value_info_group_by.txt /T{regression_test_paths["TstDir"]}/dmsscript/value_info_group_by.dmsscript /{MT1} /{MT2} /{MT3} {regression_test_paths["TstDir"]}/operator/cfg/MicroTst.dms t1642_value_info_group_by", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1642_value_info_group_by.txt")

    # t1742 — command-line @statistics op de Operator-config (/Arithmetics/UnTiled/add/attr);
    #         vergelijk gegenereerde HTML met TestReferenceFiles/t1742/Statistics_AUAA.html.
    generated_statfile = f"{local_machine_parameters["tmpFileDir"]}/t1742_command_statistics_stat.html"
    reference_statfile = f"{regression_test_paths["TestRefDir"]}/t1742/Statistics_AUAA.html"
    regression.add_exp(exps, name=f"{result_folder_name}__t1742_command_statistics", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t1742_command_statistics.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["OperatorPath"]} @statistics /Arithmetics/UnTiled/add/attr @file {generated_statfile}", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t1742_command_statistics.txt", file_comparison=(reference_statfile, generated_statfile))
    
    # t2000 — Hestia-development (model-hestia-development.main_18_0_4): @statistics op
    #         /Jaarreeksen/hWP_asl; vergelijk met referentie-HTML in HESTIA_dev.
    generated_statfile = f"{local_machine_parameters["tmpFileDir"]}/t2000_hestia_hWP_asl_statistics.html"
    # The 20.x @statistics output prepends the unit Descr ("aantal aansluitingen:")
    # to the ValuesMetric line; 19.x does not. The statistics themselves are identical,
    # so use a version-specific reference (the _tm_v19 pattern, as for t100/t102).
    _t2000_maj = version.split(".")[0]
    _t2000_suffix = "_tm_v19" if (_t2000_maj.isdigit() and int(_t2000_maj) < 20) else ""
    reference_statfile = f"{regression_test_paths["TestRefDir"]}/t2000/t2000_hestia_hWP_asl_statistics{_t2000_suffix}.html"
    regression.add_exp(exps, name=f"{result_folder_name}__t2000_hestia_hWP_asl_statistics", cmd=f"{geodms_paths["GeoDmsRunPath"]} /L{result_paths["results_log_folder"]}/t2000_hestia_hWP_asl_statistics.txt /{MT1} /{MT2} /{MT3} {regression_test_paths["HestiaDevelopment"]} @statistics /Jaarreeksen/hWP_asl @file {generated_statfile}", exp_fldr=f"{result_paths["results_folder"]}", env=env_vars, log_fn=f"{result_paths["results_log_folder"]}/t2000_hestia_hWP_asl_statistics.txt", file_comparison=(reference_statfile, generated_statfile))
    return exps

_RELEASE_CACHE_FILENAME = "github_release_versions.json"

def _github_release_versions(cache_dir:str):
    """Return the set of full-release versions ('major.minor.patch') of
    github.com/ObjectVision/GeoDMS (pre-releases and drafts excluded), or
    None when neither the GitHub API nor a previously cached list is
    available. The list is cached in cache_dir so offline runs keep
    filtering consistently."""
    cache = Path(cache_dir) / _RELEASE_CACHE_FILENAME
    versions = None
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://api.github.com/repos/ObjectVision/GeoDMS/releases?per_page=100",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "GeoDMS-Test-regression"})
        with urllib.request.urlopen(req, timeout=10) as f:
            releases = json.load(f)
        # tag_name comes as v20.1.0 / v19.0.0.b / v17.9.5b -> keep the numeric triple
        versions = sorted({m.group(1) for r in releases
                           if not r.get("prerelease") and not r.get("draft")
                           for m in [re.match(r"v?(\d+\.\d+\.\d+)", r.get("tag_name", ""))] if m})
        cache.parent.mkdir(parents=True, exist_ok=True)
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(versions, f)
    except Exception as e:
        if cache.exists():
            print(f"[report filter] GitHub releases not reachable ({e}); using cached list {cache}")
            with open(cache, "r", encoding="utf-8") as f:
                versions = json.load(f)
        else:
            print(f"[report filter] GitHub releases not reachable ({e}) and no cache; report will show all versions")
    return set(versions) if versions is not None else None

def restrict_report_to_releases(display_version:str, tmp_file_dir:str):
    """Monkeypatch regression.get_valid_result_folders so the comparison
    report only gets columns for full GitHub releases plus the version under
    test. Result folders of pre-releases / retracted / intermediate versions
    stay on disk but are no longer shown."""
    releases = _github_release_versions(tmp_file_dir)
    if releases is None:
        return
    keep = set(releases)
    current = re.match(r"(\d+\.\d+\.\d+)", display_version)
    if current:
        keep.add(current.group(1))
    original_get_valid_result_folders = regression.get_valid_result_folders
    def _only_release_folders(version, result_paths):
        folders = original_get_valid_result_folders(version, result_paths)
        kept = [f for f in folders if regression.get_semantic_version_from_folder_name(f) in keep]
        dropped = len(folders) - len(kept)
        if dropped:
            print(f"[report filter] {dropped} result folder(s) of non-release versions hidden from the report (ReportOnlyReleases=false shows them again)")
        return kept
    regression.get_valid_result_folders = _only_release_folders

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
    # Report-generation scripts (profiler.py + regression.py) are bundled with
    # this test harness in batch/generic/ and version-controlled here, so a test
    # machine only needs [this repo] + [installed GeoDms versions] — not the
    # GeoDMS source tree. (They also ship inside each GeoDms install and live in
    # the GeoDMS repo's profiler/, but full.py uses its own bundled copy.)
    report_scripts_dir = str(Path(__file__).resolve().parent / "generic").replace("\\", "/")
    geodms_paths["GeoDmsProfilerPath"] = f"{report_scripts_dir}/profiler.py"
    geodms_paths["GeoDmsRegressionPath"] = f"{report_scripts_dir}/regression.py"
    exe = geodms_paths["GeoDmsExeSuffix"]
    # If a RunPrefix is set (e.g. "wsl --" for linux-release flavors), prepend
    # it so any consumer that just builds f"{GeoDmsRunPath} <args>" actually
    # invokes the binary through WSL rather than as a direct Windows process.
    prefix = geodms_paths["GeoDmsRunPrefix"]
    prefix_str = f"{prefix} " if prefix else ""
    geodms_paths["GeoDmsRunPath"] = f"{prefix_str}{geodms_paths["GeoDmsPath"]}/GeoDmsRun{exe}"
    geodms_paths["GeoDmsGuiQtPath"] = f"{prefix_str}{geodms_paths["GeoDmsPath"]}/GeoDmsGuiQt{exe}"
    return geodms_paths

def run_full_regression_test(version:str="20.0.1.m", MT1="S1", MT2="S2", MT3="S3"):
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
    parser.add_argument(
        "-all-versions",
        dest="all_versions",
        action="store_true",
        help=(
            "Show every historical result folder as a report column, including "
            "pre-releases and intermediate versions. Default: only full GitHub "
            "releases plus the version under test (see also ReportOnlyReleases "
            "in local_settings.json)."
        ),
    )
    parser.add_argument(
        "-linux-gui",
        dest="linux_gui",
        action="store_true",
        help=(
            "Run the GeoDmsGuiQt GUI tests (t1630/t1640/t1642) on the .l (linux) "
            "flavor too. Off by default because GUI tests hang and wedge WSL when "
            "Qt6 is missing; only pass this once Qt6 + a WSLg display are present."
        ),
    )
    parser.add_argument(
        "-report-only",
        dest="report_only",
        action="store_true",
        help=(
            "Skip running any experiments; just (re)generate the HTML report "
            "from the result folders already in ResultsBaseDir. Use after a run "
            "was interrupted before the report step, or after editing the report "
            "renderer, to refresh the report without re-running the suite."
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

    display_version = geodms_paths["GeoDmsDisplayVersion"]

    report_only_releases = str(_load_local_settings().get("ReportOnlyReleases", True)).lower() not in ("false", "0", "no", "")
    if report_only_releases and not args.all_versions:
        restrict_report_to_releases(display_version, local_machine_parameters["tmpFileDir"])

    regression_test_paths = get_regression_test_paths(local_machine_parameters)
    result_paths = regression.get_result_paths(geodms_paths, regression_test_paths, display_version, MT1, MT2, MT3)

    # Redirect result storage out of the working copy when ResultsBaseDir is set
    # (see _BUILT_IN_DEFAULTS / local_settings.json). This keeps the ~GB result
    # history and the HTML report in a shared location so multiple working
    # copies / users on this machine accumulate into one comparison set.
    results_base = _load_local_settings().get("ResultsBaseDir")
    if results_base:
        folder_name = regression.get_result_folder_name(display_version, geodms_paths, MT1, MT2, MT3)
        result_paths["results_base_folder"] = results_base
        result_paths["results_folder"] = f"{results_base}/{folder_name}"
        result_paths["results_log_folder"] = f"{result_paths["results_folder"]}/log"
        os.makedirs(result_paths["results_log_folder"], exist_ok=True)
    #remove_local_data_dir_regression(local_machine_parameters["LocalDataDirRegression"])
    #import_module_from_path(geodms_paths["GeoDmsProfilerPath"])

    # Report-only: skip building/running experiments entirely and just rebuild
    # the HTML report from the result folders already on disk. The report uses
    # the same release-filter + ResultsBaseDir setup as a real run, so the
    # output is identical to what a completed run would have produced.
    if args.report_only:
        print("-report-only: regenerating HTML report from existing result folders (no experiments run)")
        regression.collect_and_generate_test_results(display_version, result_paths)
        return

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
        # GUI tests (GeoDmsGuiQt) historically needed Qt6, which used to be absent
        # in WSL. They don't just fail -- they hang and, when killed, wedge WSL so
        # every following test reports "sampler produced no rows" (cascade). So they
        # are skipped on .l by default. Pass -linux-gui to run them anyway once Qt6
        # (libqt6{core,gui,widgets,svg}6) and a WSLg display (DISPLAY/wayland) are in
        # place; the per-test timeout + wsl --shutdown (profiler) contain a hang.
        gui_exps = [e for e in operator_experiments if "GeoDmsGuiQt" in (e.command or "")]
        if gui_exps and not args.linux_gui:
            print(f"linux flavor: skipping {len(gui_exps)} GUI test(s) (GeoDmsGuiQt; pass -linux-gui to run on .l): "
                  + ", ".join(e.name.split('__', 1)[-1] for e in gui_exps))
            operator_experiments = [e for e in operator_experiments if "GeoDmsGuiQt" not in (e.command or "")]
        elif gui_exps:
            print(f"linux flavor: -linux-gui set -> running {len(gui_exps)} GUI test(s) on .l: "
                  + ", ".join(e.name.split('__', 1)[-1] for e in gui_exps))

        # Heavy .l tests whose working set exceeds this host's RAM swap-thrash through
        # WSL and never finish in practice (raising the WSL memory cap only delays the
        # wall -- the working set exceeds total host RAM). On Windows the OS page file
        # absorbs the overflow so they still pass on .m; this is .l-only. So skip them
        # when the host has too little RAM. Detection failure -> do not skip.
        #   t2000 (Hestia)  ~73 GB working set  -> needs a >=96 GB box (e.g. Maarten's 128 GB).
        #   t641  (RSopen) ~155 GB working set  -> its drvfs BaseData-write failure is fixed
        #         (ext4 relocation below), but once PAST the writes the allocation phase
        #         balloons to ~155 GB (44 GB RSS + 111 GB swap) and thrashes on this 64 GB
        #         host (~5% CPU, log frozen). Even a 128 GB box swaps; ~192 GB to run clean.
        _HEAVY_L_MIN_HOST_GB = {"t2000": 96, "t641": 192}
        try:
            import psutil
            _host_gb = psutil.virtual_memory().total / (1024 ** 3)
        except Exception:
            _host_gb = None
        if _host_gb is not None:
            for _tag, _min_gb in _HEAVY_L_MIN_HOST_GB.items():
                if _host_gb < _min_gb and any(_tag in e.name for e in operator_experiments):
                    print(f"linux flavor on a {_host_gb:.0f} GB host: skipping {_tag} "
                          f"(working set > host RAM; needs a >={_min_gb} GB machine)")
                    operator_experiments = [e for e in operator_experiments if _tag not in e.name]

        # %LocalDataProjDir% holds each project's writable working data (CalcCache
        # + generated BaseData). For t641 (RSopen) that is GBs of libtiff TIFs;
        # on .l it resolves to /mnt/c/... (drvfs), where large sequential strip
        # writes sporadically fail ("gdal Failure: TIFFAppendToStrip: Write error
        # at scanline N" — a drvfs/9p write-reliability limit, not disk-full) and
        # are very slow. Relocate the RSopen projdir onto a WSL-native ext4 path so
        # those writes land on ext4 (reliable + fast). tmpFileDir, results_folder.txt
        # and %LocalDataDir% stay on /mnt/c: small reads, and written by this
        # (Windows) python process, which cannot write into the distro's ext4 fs.
        wsl_projdir_base  = to_wsl_path(local_machine_parameters["LocalDataDirRegression"])  # /mnt/c/LocalData/regression
        ext4_projdir_base = "/root/regression"  # ext4 (WSL default user = root); ~950 GB free on the D:\WSL distro disk

        for exp in operator_experiments:
            # Inject /SH (RSF_ShowThousandSeparator) so number formatting in
            # Linux-produced output (statistics HTML, test_log strings) matches
            # the reference files captured on Windows where the dev's persistent
            # registry setting has thousand-separator on. Insert just after the
            # last /S<N> multithreading flag.
            cmd = exp.command
            for tail in (" /S3 ", " /S2 ", " /S1 "):
                if tail in cmd:
                    cmd = cmd.replace(tail, tail.rstrip() + " /SH ", 1)
                    break
            exp.command = to_wsl_path(cmd)
            if exp.environment_variables:
                ev = to_wsl_path(exp.environment_variables)
                # t641 (RSopen) writes GBs of BaseData TIFs under %LocalDataProjDir%;
                # keep those off drvfs (see above). Anchored on the LOCALDATAPROJDIR
                # assignment so the sibling /mnt/c paths (tmpFileDir, …) are untouched.
                if "t641" in exp.name:
                    ev = ev.replace(
                        f"GEODMS_DIRECTORIES_LOCALDATAPROJDIR={wsl_projdir_base}",
                        f"GEODMS_DIRECTORIES_LOCALDATAPROJDIR={ext4_projdir_base}")
                # Build WSLENV listing every variable name so wsl.exe propagates
                # them (without /p — we've already translated paths ourselves).
                names = [pair.split('=', 1)[0].strip()
                         for pair in ev.split(';') if '=' in pair]
                ev = ev + ';WSLENV=' + ':'.join(names)
                exp.environment_variables = ev

        # The relocated ext4 projdir must exist before GeoDMS writes into it, and
        # the issue-1101 non-ASCII .fss cleanup (done for the /mnt/c copy by
        # workaround_issue_1101 above) must also cover the ext4 copy so repeat runs
        # keep fresh-create semantics. Best-effort — never abort the run on this.
        if any("t641" in e.name for e in operator_experiments):
            ext4_rsopen = f"{ext4_projdir_base}/RSopen_RegressieTest_v2025"
            stale = " ".join(f"'{ext4_projdir_base}/{rel}'" for rel in _ISSUE_1101_AFFECTED_FSS)
            try:
                subprocess.run(["wsl", "--", "bash", "-c",
                                f"mkdir -p '{ext4_rsopen}'; rm -rf {stale}"], check=False)
            except OSError as e:
                print(f"[.l projdir] could not prepare {ext4_rsopen}: {e}")

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