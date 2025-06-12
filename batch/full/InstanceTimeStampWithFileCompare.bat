Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %6

Set GeoDmsLogFilePath=%results_log_folder%\%6.txt
del %GeoDmsLogFilePath% 2>nul
Call full/SetStartTime.bat

Echo.

Call full/EchoAndExecute.bat %1 %2 %3 %4 %5 

Call full/SetEndTime.bat

Set resultfile=%results_folder%\%6.txt
Echo "%resultfile%"

Echo write to "%resultfile%"
Echo ^<description^>%6%:^<^/description^>^<result^> > "%resultfile%"

Echo.
Echo FileCompare Execute: FC %7 %8
FC %7 %8 > NUL && Echo Ok, all files are identical >> "%resultfile%" || Echo False, difference(s) occur  >> "%resultfile%"

Echo ^<^/result^>^ >> "%resultfile%"

Call full/WriteTimeStamps.bat "%resultfile%"



