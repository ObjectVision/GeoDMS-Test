REM paden die worden afgeleid

Set prj_snapshotsDir=C:\ProjDir_Jip\prj_snapshots

Rem projecten die uit het GeoDMS tst project

Rem bepaal de TstDir, relatief vanuit de BatchDir
set BatchDir=%CD%
cd ..
set TstDir=%CD%
cd %BatchDir%
set RegressionTestsSourceDataDir=C:/SourceData/RegressionTests

Set OperatorPath=%TstDir%\Operator\cfg\Operator.dms
Set StoragePath=%TstDir%\Storage\cfg\Regression.dms
Set StorageGDALPath=%TstDir%\Storage_gdal\cfg\Regression.dms

Set RegressionPath=%TstDir%\Regression\cfg\stam.dms

Set BLRDConversiePath=%prj_snapshotsDir%\bl_rd_conversie\cfg\root.dms

Rem projecten uit de prj_snapshots 
Set LusDemoRunPath2023=%prj_snapshotsDir%\lus_demo_2023\cfg\demo.dms
Set RSLRunPath=%prj_snapshotsDir%\RSL_2020\cfg\regression_test.dms
Set RSLight_2020Path=%prj_snapshotsDir%\RSLight_2020\cfg\Regression_test.dms
Set HestiaRunPath=%prj_snapshotsDir%\Hestia2024\Runs\HestiaRun.dms

Set TwoUPRunPath=%prj_snapshotsDir%\2UP\cfg\stam.dms
Set TwoBURPRunPath=%prj_snapshotsDir%\2BURP\cfg\main.dms
Set DynaPopPath=%prj_snapshotsDir%\100m_DynaPop\cfg\StatusQuo.dms
Set RSLight_2021Path=%prj_snapshotsDir%\RSLight2021_ontwikkel_2
Set RSLight2021_ontwikkel_3Path=%prj_snapshotsDir%\RSLight2021_ontwikkel_3

Set BAG20MakeSnapShotPath=%prj_snapshotsDir%\BAG20\cfg\BAG20_MakeSnaphot.dms

Rem Brondata voor projecten
Set RslDataDir=%RegressionTestsSourceDataDir%\RSL
Set HestiaDataDir=%RegressionTestsSourceDataDir%\Hestia
Set CusaRunPath=%prj_snapshotsDir%\geodms_africa_cusa2\cfg\africa.dms
Set RSopen_RegressieTestPath=%prj_snapshotsDir%\RsOpen_regressietest\cfg
Set Networkmodel_pbl_regressietest=%prj_snapshotsDir%\NetworkModel_PBL_RegressieTest\cfg
Set Networkmodel_eu_regressietest=%prj_snapshotsDir%\networkmodel_eu_regressieTest\cfg

