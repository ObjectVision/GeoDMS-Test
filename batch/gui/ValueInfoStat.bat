Rem Gui test of issue 887

set ProjDir=..\Operator
set CalcCacheDir=%ProjDir%\CalcCache
set logfile=!tmpFileDir!\ValueInfoStat.log
del %logfile% 2>nul

if [%1] neq [] set MT1=%1
if [%2] neq [] set MT2=%2
if [%3] neq [] set MT3=%3

echo "%GeoDmsGuiPath%"  /%MT1% /%MT2% /%MT3% >> %logfile%
START	"GeoDmsGui" /MAX "%GeoDmsGuiPath%" /%MT1% /%MT2% /%MT3% "%projDir%\cfg\issue_1438.dms"

REM Wait 1 secs (2 pings with 1 sec intervals between them to localhost)
ping 127.0.0.1 -n 2 > nul

REM Send cmd 2 (WM->Focus) with requires 3 subsequent integers representing code, WPARAM and LPARAM
REM code 258 represents WM_CHAR, 13 = VK_RETURN; TreeView requires WM_CHAR
REM "%GeoDmsGuiPath%" /A SEND 2 3 258 13 0
REM Send cmd 5: mfGeneral.miDefaultView.Click;
REM "%GeoDmsCallerPath%" WAIT 10

REM "%GeoDmsCallerPath%" GOTO "/vrz_20201009/Geometry"
"%GeoDmsCallerPath%" GOTO "/vrz_20201009/Geometry"
ping 127.0.0.1 -n 2 > nul

REM Activate DP Statistics
"%GeoDmsCallerPath%" DP 4 >> %logfile%

ping 127.0.0.1 -n 15 > nul

REM Send cmd 0 (WM->null)
REM Send cmd 1 (WM->Main) 16 represents WM_COMMAND TB_INFO
ping 127.0.0.1 -n 5 > nul
REM pause "Next step: SAVE_DP"
"%GeoDmsCallerPath%" SAVE_DP "!results_folder!/t1642_value_info_stat.tmp" >> %logfile%


REM pause

REM Send cmd 0 (WM->null)
REM Send cmd 1 (WM->Main) 16 represents WM_CLOSE.
ping 127.0.0.1 -n 5 > nul
REM pause "Next step: WM_CLOSE"
"%GeoDmsCallerPath%" SEND 1 3 16 0 0 >> %logfile%

%GeoDmsRunCmdBaseLarge% /%1 /%2 %RegressionPath% /results/t1642_value_info_stat/result_html


