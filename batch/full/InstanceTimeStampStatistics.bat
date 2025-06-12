Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %6

Call full/SetStartTime.bat
Set statfile=%tmpFileDir%\%6_stat.html
Set GeoDmsLogFilePath=%results_log_folder%\%6.txt

Set command=%GeoDmsRunCmdBaseLarge% /L"%GeoDmsLogFilePath%" /%1 /%2 /%3 %4 @statistics %5 @file %statfile%
Echo.
Echo Execute: %command%

%command%

Set resultfile=%results_folder%\%6.txt
echo del "%resultfile%"
del "%resultfile%"
rem pause
Echo ^<description^>%5^</description^> > "%resultfile%"
Echo.

Echo FileCompare Execute: FC %statfile% %7
FC %statfile% %7 > NUL && Echo ^<I^>result:^</I^> ^<B^>OK^</B^> >> "%resultfile%" || Echo ^<I^>result:^</I^> ^<B^>False^</B^> , difference(s) occur, errorcode: %errorlevel%  >> "%resultfile%"

Echo ^<^/result^>^ >> "%resultfile%"

Call full/SetEndTime.bat

Call full/WriteTimeStamps.bat "%results_folder%\%6.txt"

