Rem Gui test of issue 887

REM set ProjDir=..\Operator
REM set CalcCacheDir=%ProjDir%\CalcCache
set logfile=!LogFileDir!\MapViewClassification.log
del logile 2>nul

REM if exist %projDir%\regr_results\strfiles del %projDir%\regr_results\strfiles\*.txt

echo "%GeoDmsGuiPath%" >> %logfile%

echo ****** Start test
echo.
echo GeoDMS Command: "GeoDmsGui" /MAX "%GeoDmsGuiPath%" "%TstDir%\operator\cfg\MicroTst.dms"

START "GeoDmsGui" /MAX "%GeoDmsGuiPath%" "%TstDir%\operator\cfg\MicroTst.dms"

REM Wait 1 secs (2 pings with 1 sec intervals between them to localhost)
REM ping 127.0.0.1 -n 2 > nul

REM Send cmd 2 (WM->Focus) with requires 3 subsequent integers representing code, WPARAM and LPARAM
REM code 258 represents WM_CHAR, 13 = VK_RETURN; TreeView requires WM_CHAR
REM "%GeoDmsGuiPath%" /A SEND 2 3 258 13 0
REM Send cmd 5: mfGeneral.miDefaultView.Click;
"%GeoDmsCallerPath%" WAIT 10 >> %logfile%
"%GeoDmsCallerPath%" GOTO "/BackGroundLayer/district/hoek" >> %logfile%

REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 5 0 >> %logfile%
REM "%GeoDmsCallerPath%" SEND 5 1 0 >> %logfile% && REM code 5: dmfGeneral.miDefaultView.Click;

REM Send cmd 4 (WM_COPYDATA->MdiChild)
REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" WAIT 10 >> %logfile%
"%GeoDmsCallerPath%" SEND 4 2 1 11 >> %logfile% && REM code 1 (activates popup menu on active control) and menu item list {11}: Edit Palette
REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" WAIT 10 >> %logfile%
"%GeoDmsCallerPath%" SEND 4 2 0 4 >> %logfile%  && REM code 0 (activate sub-object) with sequence {4}: the Numeric Class Count control of the Palette Editor

REM Send cmd 3 (WM->MdiChild)
REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 3 3 258 52 0 >> %logfile% && REM 258=WM_CHAR, 52='4'
REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 3 3 256 13 0 >> %logfile% && REM 256=WM_KEYDOWN, 13=VK_RETURN

REM activate popup menus on active control of MdiChild
REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 4 3 1 1 2 >> %logfile% && REM menu item list {1 2} Classify hoek->Equal Count)

REM "%GeoDmsCallerPath%" SEND 4 3 1 1 1 >> %logfile% && REM menu item list (1 1) Classify hoek->Unique values

REM activate the sub-object with sequence {6 1 1 3}: EditPalette/TableView/ScrollPort/TableHeader/3rdColum
REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 4 5 0 6 1 1 3 >> %logfile%

REM menu item list {7}. Copy Palette
REM ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 4 2 1 7 >> %logfile%

REM Send cmd 0 (WM->null)
REM Send cmd 1 (WM->Main) 16 represents WM_CLOSE.
ping 127.0.0.1 -n 5 > nul
"%GeoDmsCallerPath%" SEND 1 3 16 0 0 >> %logfile%

echo.
echo ****** End test
echo.
