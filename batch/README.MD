# Introduction
This document describes how to setup geodms regression testing on a new machine.

# Full regression test
The entrypoint for running the full regression test for geodms is the python script full.py. The entryfunction has the following signature:

```shell
python full.py -version 17.4.6 -MT1 S1 -MT2 S2 -MT3 S3
```

Recommended python version: 3.11+ or latest, required python modules: psutil, bs4, packaging, bokeh

The full regression tests has a series of environment variables that will be used mostly by geodms to resolve paths for projects. The following is a list of paths that should be adapted to the users specific machine situation:
In full.py: 
- "GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"
- "tmpFileDir"
- "projectsDir"
- "BatchDir"
- "TstDir"
- "OperatorPath"
- "StoragePath"
- "StorageGDALPath"
- "RegressionPath"
- "BLRDConversiePath"
- "LusDemoRunPath2023"  
- "RSLight_2020Path"
- "TwoUPRunPath"    
- "TwoBURPRunPath"
- "DynaPopPath"
- "BAG20MakeSnapShotPath"
- "RSopen_RegressieTestPath_v2025"
- "Networkmodel_pbl_regressietest"
- "Networkmodel_eu_regressietest"
- "GEODMS_Overridable_HestiaDataDir"
- "RegressionTestsSourceDataDir"
- "GEODMS_Overridable_RSo_DataDir"
- "GEODMS_Overridable_RS_Lb_DataDir"
- "GEODMS_Overridable_PrivDataDir"
- "GEODMS_Overridable_CUSA2_DataDir"
- "GEODMS_Overridable_ToBURPDataDir"
- "GEODMS_DIRECTORIES_LOCALDATAPROJDIR"
- "GEODMS_Overridable_MondiaalDataDir"
- "GEODMS_Overridable_NetworkModel_Dir"
- "GEODMS_Overridable_NetworkModelDataDir"

in generic/regression.py in function get_geodms_paths:
- "GeoDmsProfilerPath"

# Per-machine settings (local_settings.json)

Copy `local_settings.json.template` to `local_settings.json` (gitignored) and
adjust the SourceData/LocalData/Results paths and, for `-version local-*`
dev-build runs, `ProfilerDir` (its parent = the GeoDMS source repo; the msbuild
Release build lands in `<repo>/bin/Release/x64`). Known machines:

- **OVSRV05**: SourceData `D:/SourceData`, LocalData `C:/LocalData`, results
  `C:/LocalData/GeoDMS_Test_Results`.
- **OVSRV08**: RegressionTests-SourceData `D:/SourceData/RegressionTests`
  (no TestReferenceFiles on this machine, so reference-comparing tests cannot
  verify here), LocalData `C:/LocalData`, dev repo `C:/Dev/GeoDMS_2026`;
  the t020 polygon data lives at `E:/SourceData/RuimteScanner/SD/RSOpen`
  (override with `GEODMS_Overridable_PolyDataDir` on other machines).

# Claude / agent sessions

Project instructions for Claude Code live in the repo root `CLAUDE.md`
(committed, so they travel to every machine). Machine-independent working
agreements (commit bundling, issue etiquette, report-cell content rules) are
kept there as well — per-machine Claude memory only holds session context.


    
