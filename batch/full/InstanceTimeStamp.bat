Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %6

Set GeoDmsLogFilePath=%results_log_folder%\%6.txt
del %GeoDmsLogFilePath% 2>nul
Call full/SetStartTime.bat

Echo.
REM pause
Call full/EchoAndExecute.bat %1 %2 %3 %4 %5 

Call full/SetEndTime.bat

Call full/WriteTimeStamps.bat "%results_folder%\%6.txt"




