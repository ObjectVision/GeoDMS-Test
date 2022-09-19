REM Testen van GUI elemenenten, deels visueel, deels met output

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\gui

Call Gui\MapViewClassification.bat 
timeout /t 3

Call Full\InstanceTimeStampGUI.bat C1 C2 %RSLight_2020Path% t1630_expandtest/C1C2 t1630_expandtest_C1C2 Gui\RSLight_2020_Expand.bat
timeout /t 3
Call Full\InstanceTimeStampGUI.bat S1 C2 %RSLight_2020Path% t1630_expandtest/S1C2 t1630_expandtest_S1C2 Gui\RSLight_2020_Expand.bat
timeout /t 3
Call Full\InstanceTimeStampGUI.bat S1 S2 %RSLight_2020Path% t1630_expandtest/S1S2 t1630_expandtest_S1S2 Gui\RSLight_2020_Expand.bat
timeout /t 3
Call Full\InstanceTimeStampGUI.bat C1 S2 %RSLight_2020Path% t1630_expandtest/C1S2 t1630_expandtest_C1S2 Gui\RSLight_2020_Expand.bat
timeout /t 3

Call Full\InstanceTimeStampGUI.bat %Setting1% %Setting2% %OperatorPath% value_info_agg t1640_value_info_agg Gui\ValueInfo.bat
timeout /t 3

Call Full\InstanceTimeStampGUI.bat %Setting1% %Setting2% %OperatorPath% value_info_stat t1642_value_info_stat Gui\ValueInfoStat.bat
timeout /t 3


Call Full\InstanceTimeStampStatistics.bat %Setting1% %Setting2% %OperatorPath% /Arithmetics/UnTiled/add/attr t1742_command_statistics "%TstDir%\norm\Statistics_AUAA.txt"

