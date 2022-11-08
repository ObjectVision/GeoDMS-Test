Rem Unit Gui test for Error in general detail page with explicit suppliers

Set RegrResult=OK

Echo ****************
Echo.
Echo Test: GeoDMS Command: %GeoDmsGuiPath% %TstDir%\Unit\GUI\cfg\DPGeneral_explicit_supplier_error.dms
Echo.

START	"GeoDmsGui" /MAX "%GeoDmsGuiPath%" "%TstDir%\Unit\GUI\cfg\DPGeneral_explicit_supplier_error.dms"

ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" GOTO "/DPGeneral_explicit_supplier_error/test" 

Echo Activate Detail Page General
"%GeoDmsCallerPath%" DP 0

ping 127.0.0.1 -n 2 > nul
Set ResultFolder=%localDataDir%\GeoDMSTestResults\Unit\GUI
IF not exist %ResultFolder% (mkdir %ResultFolder%)

del %ResultFolder%\DPGeneral_explicit_supplier_error.tmp 2>nul
del %ResultFolder%\DPGeneral_ES_error.txt 2>nul

Echo write results to: %ResultFolder%\DPGeneral_explicit_supplier_error.tmp
"%GeoDmsCallerPath%" SAVE_DP "%ResultFolder%\DPGeneral_explicit_supplier_error.tmp" 

ping 127.0.0.1 -n 2 > nul
"%GeoDmsCallerPath%" SEND 1 3 16 0 0

