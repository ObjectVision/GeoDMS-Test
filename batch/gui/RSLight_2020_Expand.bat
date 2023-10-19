Rem Gui test of issue 887, expanding subitems of SourceData/Claims/ReadData of RSLight_2020 configuration
set logfile=!tmpFileDir!\RSLight_2020_expand.log

del %logfile% 2>nul

echo "%GeoDmsGuiPath%" >> %logfile%
break

set CONFIG=%RSLight_2020Path%
set ITEM=t1630_expandtest/result_html
if [%1] neq [] set MT1=%1
if [%2] neq [] set MT2=%2
if [%3] neq [] set MT3=%3
if [%4] neq [] set CONFIG=%4
if [%5] neq [] set ITEM=%5

REM START "GeoDmsGui" /MAX "%GeoDmsGuiPath%" "%RSLight_2020Path%"
echo ****** Start test
echo.
echo GeoDMS Command: "GeoDmsGui" /MAX "%GeoDmsGuiPath%" /%MT1% /%MT2% /%MT3% "%CONFIG%"
START "GeoDmsGui" /MAX "%GeoDmsGuiPath%" /%MT1% /%MT2% /%MT3% "%CONFIG%"


REM Send cmd 2 (WM->Focus) with requires 3 subsequent integers representing code, WPARAM and LPARAM
REM code 258 represents WM_CHAR, 13 = VK_RETURN; TreeView requires WM_CHAR
REM "%GeoDmsGuiPath%" /A SEND 2 3 258 13 0
REM Send cmd 5: mfGeneral.miDefaultView.Click;

ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" GOTO "SourceData/Claims/ReadData" >> %logfile%

ping 127.0.0.1 -n 2 > nul
REM tvTreeItem.Selected.Expand(true)
"%GeoDmsCallerPath%" SEND 8 1 1 >> %logfile%

ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" GOTO %ITEM% >> %logfile%
ping 127.0.0.1 -n 2 > nul
REM code 5: dmfGeneral.miDefaultView.Click;
"%GeoDmsCallerPath%" SEND 5 1 0 >> %logfile%

ping 127.0.0.1 -n 2 > nul
REM Send cmd 1 (WM->Main) 16 represents WM_CLOSE.
"%GeoDmsCallerPath%" SEND 1 3 16 0 0 >> %logfile%

echo.
echo ****** End test
echo.
