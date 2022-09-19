SETLOCAL EnableDelayedExpansion

Call Full/SetStartTime.bat

Call Gui\GuiTest_issue1429.bat %1 %2 %3 %4 %5
echo.

cd %BatchDir%

Call Full/SetEndTime.bat
Call Full/WriteTimeStamps.bat %1 %2 %3 %4 %results_folder%\%5.txt


