SETLOCAL EnableDelayedExpansion

Call full/SetStartTime.bat

Call Gui/GuiTest_issue1438.bat
%GeoDmsRunCmdBaseLarge% /%1 /%2 %RegressionPath% /results/t1642_value_info_stat/result_html

echo.

cd %BatchDir%

Call full/SetEndTime.bat
Call full/WriteTimeStamps.bat %1 %2 %3 %4 %results_folder%\%5.txt


