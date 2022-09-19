Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %5

Call full/SetStartTime.bat

Echo.

Call full/EchoAndExecute.bat %1 %2 %3 %4 

Call full/SetEndTime.bat

Set resultfile=%results_folder%\%5.txt
Echo %resultfile%

Echo write to %resultfile%
Echo ^<description^>%5%:^<^/description^>^<result^> > %resultfile%

Echo.
Echo FileCompare Execute: FC %6 %7
FC %6 %7 > NUL && Echo Ok, all files are identical >> %resultfile% || Echo False, difference(s) occur  >> %resultfile%

Echo ^<^/result^>^ >> %resultfile%

Call full/WriteTimeStamps.bat %resultfile%



