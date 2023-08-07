Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %6

Call full/SetStartTime.bat

Echo.
Echo Execute: %GeoDmsRunCmdBaseLarge% /%1 /%2 /%3 %4 @statistics %5 @file %LogFileDir%\%6_stat.txt

%GeoDmsRunCmdBaseLarge% /%1 /%2 /%3 /CH %4 @statistics %5 @file %LogFileDir%\%6_stat.txt  >> !LogFileDir!\GeoDMSlog.txt

Set resultfile=%results_folder%\%6.txt


Echo ^<description^>%5^</description^> > %resultfile%
Echo.

Echo FileCompare Execute: FC %LogFileDir%\%6_stat.txt %7
FC %LogFileDir%\%6_stat.txt %7 > NUL && Echo ^<I^>result:^</I^> ^<B^>OK^</B^> >> %resultfile% || Echo ^<I^>result:^</I^> ^<B^>False^</B^> , difference(s) occur, errorcode: %errorlevel%  >> %resultfile%

Echo ^<^/result^>^ >> %resultfile%

Call full/SetEndTime.bat

Call full/WriteTimeStamps.bat %results_folder%\%6.txt

