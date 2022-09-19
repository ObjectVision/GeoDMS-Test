Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %5

Call Full/SetStartTime.bat

Echo.
Echo Execute: %6  /%1 /%2 %3 %4 

Call %6 %1 %2 %3 %4 %5

Call Full/SetEndTime.bat

Call Full/WriteTimeStamps.bat %results_folder%\%5.txt


