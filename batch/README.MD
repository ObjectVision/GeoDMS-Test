# Introduction
This document describes how to setup geodms regression testing on a new machine.

# Full regression test
The entrypoint for running the full regression test for geodms is the python script full.py. The entryfunction has the following signature:

```shell
python full.py -version 17.4.6 -MT1 S1 -MT2 S2 -MT3 S3
```

The full regression tests has a series of environment variables that will be used mostly by geodms to resolve paths for projects. The following is a list of paths that should be adapted to the users specific machine situation:
In full.py: 
- "GEODMS_OVERRIDABLE_RegressionTestsSourceDataDir"
- "tmpFileDir"
- "prj_snapshotsDir"
- "BatchDir"
- "TstDir"
- "OperatorPath"
- "StoragePath"
- "StorageGDALPath"
- "RegressionPath"
- "BLRDConversiePath"
- "LusDemoRunPath2023"  
- "RSLRunPath"  
- "RSLight_2020Path"
- "HestiaRunPath"
- "TwoUPRunPath"    
- "TwoBURPRunPath"
- "DynaPopPath"
- "RSLight_2021Path"
- "RSLight2021_ontwikkel_3Path"
- "BAG20MakeSnapShotPath"
- "RSopen_RegressieTestPath"
- "RSopen_RegressieTestPath_v2025"
- "Networkmodel_pbl_regressietest"
- "Networkmodel_eu_regressietest"
- "GEODMS_Overridable_RslDataDir"
- "GEODMS_Overridable_HestiaDataDir"
- "RegressionTestsSourceDataDir"
- "GEODMS_Overridable_RSo_DataDir"
- "GEODMS_Overridable_RVF_DataDir"
- "GEODMS_Overridable_RSo_PrivDataDir"
- "GEODMS_Overridable_PrivDataDir"
- "GEODMS_Overridable_ToBURPDataDir"
- "GEODMS_DIRECTORIES_LOCALDATAPROJDIR"
- "GEODMS_Overridable_MondiaalDataDir"
- "GEODMS_Overridable_NetworkModel_Dir"
- "GEODMS_Overridable_NetworkModelDataDir"

in generic/regression.py in function get_geodms_paths:
- "GeoDmsPath"
- "GeoDmsProfilerPath"


    
