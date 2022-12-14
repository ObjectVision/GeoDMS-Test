REM paden die worden afgeleid

Set prj_snapshotsDir=%RegressionTestsSourceDataDir%\prj_snapshots

Rem projecten die uit het GeoDMS tst project

Rem bepaal de TstDir, relatief vanuit de BatchDir
set BatchDir=%CD%
cd ..
set TstDir=%CD%
cd %BatchDir%

Set OperatorPath=%TstDir%\Operator\cfg\Operator.dms
Set StoragePath=%TstDir%\Storage\cfg\Regression.dms
Set StorageGDALPath=%TstDir%\Storage_gdal\cfg\Regression.dms

Set RegressionPath=%TstDir%\Regression\cfg\stam.dms

Rem projecten uit de prj_snapshots 
Set VestaRunPath=%prj_snapshotsDir%\VestaProductie\Runs\regression_test.dms
Set LusDemoRunPath=%prj_snapshotsDir%\lus_demo\cfg\regression_test.dms
Set LusDemoRunPath2022=%prj_snapshotsDir%\lus_demo_2022\cfg\demo.dms
Set RSLRunPath=%prj_snapshotsDir%\RSL_2020\cfg\regression_test.dms
Set RSLight_2020Path=%prj_snapshotsDir%\RSLight_2020\cfg\Regression_test.dms
Set SawecRunPath=%prj_snapshotsDir%\Sawec\Runs\ReferentiePerJaar.dms
Set TwoUPRunPath=%prj_snapshotsDir%\2UP\cfg\stam.dms
Set DynaPopPath=%prj_snapshotsDir%\100m_DynaPop\cfg\StatusQuo.dms
Set RSLight_2021Path=%prj_snapshotsDir%\RSLight2021_ontwikkel_2
Set RSLight2021_ontwikkel_3Path=%prj_snapshotsDir%\RSLight2021_ontwikkel_3

Set BAG20MakeSnapShotPath=%prj_snapshotsDir%\BAG20\cfg\BAG20_MakeSnaphot.dms

Rem Brondata voor projecten
Set RslDataDir=%RegressionTestsSourceDataDir%\RSL
Set HestiaDataDir=%RegressionTestsSourceDataDir%\Hestia

