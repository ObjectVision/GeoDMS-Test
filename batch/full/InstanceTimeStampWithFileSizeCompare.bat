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
Echo %resultfile%

Echo write to %resultfile%
Echo ^<description^>%6%:^<^/description^>^<result^> > %resultfile%
Echo.

FOR %%A IN (%7) DO (
	SET CFileSize=%%~zA
)
ECHO FileSize %7 : !CFileSize!

FOR %%B IN (%8) DO (
	SET RFileSize=%%~zB
)
ECHO FileSize %8 : !RFileSize!

Echo.

if !CFileSize! EQU !RFileSize! (
    echo OK, file size equals
    echo OK, file size equals >> !resultfile!
) else (
    echo False, file size differs
    echo False, file size differs >> !resultfile!
)

Echo ^<^/result^>^ >> %resultfile%

Call full/WriteTimeStamps.bat %resultfile%