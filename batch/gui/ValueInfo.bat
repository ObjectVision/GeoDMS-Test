Rem Gui test of issue 887

set ProjDir=..\Operator
set CalcCacheDir=%ProjDir%\CalcCache
set logfile=!tmpFileDir!\ValueInfo.log
del %logfile% 2>nul

if exist %projDir%\regr_results\strfiles del %projDir%\regr_results\strfiles\*.txt

if [%1] neq [] set MT1=%1
if [%2] neq [] set MT2=%2
if [%3] neq [] set MT3=%3

echo "%GeoDmsGuiPath%" >> %logfile%
echo GeoDmsGui" /MAX "%GeoDmsGuiPath%" /%MT1% /%MT2% /%MT3% "%projDir%\cfg\operator.dms"
START	"GeoDmsGui" /MAX "%GeoDmsGuiPath%" /%MT1% /%MT2% /%MT3% "%projDir%\cfg\operator.dms"

REM Wait 1 secs (2 pings with 1 sec intervals between them to localhost)
ping 127.0.0.1 -n 2 > nul

REM Send cmd 2 (WM->Focus) with requires 3 subsequent integers representing code, WPARAM and LPARAM
REM code 258 represents WM_CHAR, 13 = VK_RETURN; TreeView requires WM_CHAR
REM "%GeoDmsGuiPath%" /A SEND 2 3 258 13 0 >> %logfile%
REM Send cmd 5: mfGeneral.miDefaultView.Click;
REM "%GeoDmsCallerPath%" WAIT 10 >> %logfile%

"%GeoDmsCallerPath%" GOTO "/Aggregations/UnTiled2UnTiled/min/att_string" >> %logfile%



REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 5 0 >> %logfile% && REM code 5: dmfGeneral.miDefaultView.Click;
REM "%GeoDmsCallerPath%" SEND 11 0 >> %logfile% && REM code 11 dmfGeneral.miDataGridView.Click;
REM "%GeoDmsCallerPath%" SEND 12 0 >> %logfile% && REM code 11 dmfGeneral.miDataGridView.Click;
REM pause

pause

"%GeoDmsCallerPath%" SEND 3 3 256 36 0 >> %logfile% && REM 256=WM_KEYDOWN, 13=VK_HOME >> %logfile%



REM Send cmd 0 (WM->null)
REM Send cmd 1 (WM->Main) 16 represents WM_COMMAND TB_INFO
ping 127.0.0.1 -n 5 > nul
"%GeoDmsCallerPath%" SEND 3 3 273 9 0 >> %logfile%


REM Send cmd 0 (WM->null)
REM Send cmd 1 (WM->Main) 16 represents WM_COMMAND TB_INFO
ping 127.0.0.1 -n 5 > nul
REM pause "Next step: SAVE_DP"
echo write results to: !results_folder!/t1640_value_info_agg.tmp/Aggregations/UnTiled2UnTiled/min/att_string	
"%GeoDmsCallerPath%" SAVE_DP "!results_folder!/t1640_value_info_agg.tmp" >> %logfile%


REM pause

REM Send cmd 0 (WM->null)
REM Send cmd 1 (WM->Main) 16 represents WM_CLOSE.
ping 127.0.0.1 -n 5 > nul
REM pause "Next step: WM_CLOSE"
"%GeoDmsCallerPath%" SEND 1 3 16 0 0 >> %logfile%

%GeoDmsRunCmdBaseLarge% /%1 /%2 %RegressionPath% /results/t1640_value_info_agg/result_html >> %logfile%


