REM Testen van GUI elemenenten, deels visueel, deels met output

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\gui

REM Call Gui\MapViewClassification.bat 
REM timeout /t 3

Call Full\GUIInstance.bat %TstDir%\dmsscript\RSLight_2020_expand_C1C2.dmsscript %RSLight_2020Path%  C1 C2 S3 t1630_expandtest_C1C2
timeout /t 3

Call Full\GUIInstance.bat %TstDir%\dmsscript\RSLight_2020_expand_C1S2.dmsscript %RSLight_2020Path%  C1 S2 S3 t1630_expandtest_C1S2
timeout /t 3


Call Full\GUIInstance.bat %TstDir%\dmsscript\RSLight_2020_expand_S1C2.dmsscript %RSLight_2020Path%  S1 C2 S3 t1630_expandtest_S1C2
timeout /t 3

Call Full\GUIInstance.bat %TstDir%\dmsscript\RSLight_2020_expand_S1S2.dmsscript %RSLight_2020Path%  S1 S2 S3 t1630_expandtest_S1S2
timeout /t 3


REM Call Full\InstanceTimeStampGUI.bat  %Setting1% %Setting2% %Setting3%  %OperatorPath% value_info_agg t1640_value_info_agg Gui\ValueInfo.bat
REM timeout /t 3

REM Call Full\InstanceTimeStampGUI.bat %Setting1% %Setting2% %Setting3%  %OperatorPath% value_info_stat t1642_value_info_stat Gui\ValueInfoStat.bat
REM timeout /t 3


Call Full\InstanceTimeStampStatistics.bat %Setting1% %Setting2% %Setting3% %OperatorPath% /Arithmetics/UnTiled/add/attr t1742_command_statistics "%TstDir%\norm\Statistics_AUAA.html"

