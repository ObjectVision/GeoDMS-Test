Rem Unit Gui test for Error in general detail page with explicit suppliers

Set command=%GeoDmsQtCmdBase% /T%TstDir%\dmsscript\DPGeneral_explicit_supplier_error.dmsscript  /S1 /S2 /S3 %TstDir%\Unit\GUI\cfg\DPGeneral_explicit_supplier_error.dms test_log %ResultDir%\unit\gui\DPGeneral_ES_error.txt 

Echo ****************
Echo.
Echo Test: %command%
Echo.

Set ResultFolder=%localDataDir%\GeoDMSTestResults\Unit\GUI
IF not exist %ResultFolder% (mkdir %ResultFolder%)

del %ResultFolder%\DPGeneral_explicit_supplier_error.tmp 2>nul

REM de Qt met het testscript
%command%

