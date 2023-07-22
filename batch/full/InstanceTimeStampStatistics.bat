Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %5

Call full/SetStartTime.bat

Echo.
Echo Execute: %GeoDmsRunCmdBaseLarge% /%1 /%2 %3 @statistics %4 @file %LogFileDir%\%5_stat.txt

%GeoDmsRunCmdBaseLarge% /%1 /%2 /CH %3 @statistics %4 @file %LogFileDir%\%5_stat.txt  >> !LogFileDir!\GeoDMSlog.txt

Set resultfile=%results_folder%\%5.txt


Echo ^<description^>%5^</description^> > %resultfile%
Echo.

Echo FileCompare Execute: FC %LogFileDir%\%5_stat.txt %6
FC %LogFileDir%\%5_stat.txt %6 > NUL && Echo ^<I^>result:^</I^> ^<B^>OK^</B^> >> %resultfile% || Echo ^<I^>result:^</I^> ^<B^>False^</B^> , difference(s) occur, errorcode: %errorlevel%  >> %resultfile%

Echo ^<^/result^>^ >> %resultfile%

Call full/SetEndTime.bat

Call full/WriteTimeStamps.bat %results_folder%\%5.txt




