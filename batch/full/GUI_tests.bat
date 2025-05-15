REM Testen van GUI elemenenten, deels visueel, deels met output

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\gui

REM Call Gui\MapViewClassification.bat 
REM timeout /t 3

REM TODO: rename dmsscript and resulting item to reflect that flags are already part of the result folder name.
Call Full\GUIInstance.bat %TstDir%\dmsscript\RSLight_2020_expand_S1S2.dmsscript %RSLight_2020Path% %Setting1% %Setting2% %Setting3% t1630_expandtest_S1S2
timeout /t 3


REM t1640_value_info
del "%LocalDataDir%\regression\t1640_value_info\t1640_value_info.tmp" 2>nul
Call full/SetStartTime.bat
Call Full\GUIInstance.bat %TstDir%\dmsscript\value_info.dmsscript %OperatorPath% %Setting1% %Setting2% %Setting3% t1640_value_info
echo %GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1640_value_info/result_html
%GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1640_value_info/result_html 
Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t1640_value_info.txt

REM t1642_value_info_group_by
del "%LocalDataDir%\regression\t1642_value_info_group_by\t1642_value_info_group_by.tmp" 2>nul
Call full/SetStartTime.bat
Call Full\GUIInstance.bat %TstDir%\dmsscript\value_info_group_by.dmsscript %TstDir%\operator\cfg\MicroTst.dms %Setting1% %Setting2% %Setting3% t1642_value_info_group_by
echo %GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1642_value_info_group_by/result_html
%GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1642_value_info_group_by/result_html 
Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t1642_value_info_group_by.txt

Call Full\InstanceTimeStampStatistics.bat %Setting1% %Setting2% %Setting3% %OperatorPath% /Arithmetics/UnTiled/add/attr t1742_command_statistics "%TstDir%\norm\Statistics_AUAA.html"

