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


REM t1640_value_info
del "%LocalDataDir%\regression\t1640_value_info\t1640_value_info.tmp" 2>nul
Call full/SetStartTime.bat
Call Full\GUIInstance.bat %TstDir%\dmsscript\value_info.dmsscript %OperatorPath%   S1 S2 S3 t1640_value_info
echo %GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1640_value_info/result_html
%GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1640_value_info/result_html 
Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t1640_value_info.txt

REM t1642_value_info_group_by
del "%LocalDataDir%\regression\t1642_value_info_group_by\t1642_value_info_group_by.tmp" 2>nul
Call full/SetStartTime.bat
Call Full\GUIInstance.bat %TstDir%\dmsscript\value_info_group_by.dmsscript %TstDir%\operator\cfg\MicroTst.dms S1 S2 S3 t1642_value_info_group_by
echo %GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1642_value_info_group_by/result_html
%GeoDmsRunCmdBaseLarge% %RegressionPath% /results/t1642_value_info_group_by/result_html 
Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %results_folder%\t1642_value_info_group_by.txt

Call Full\InstanceTimeStampStatistics.bat %Setting1% %Setting2% %Setting3% %OperatorPath% /Arithmetics/UnTiled/add/attr t1742_command_statistics "%TstDir%\norm\Statistics_AUAA.html"

