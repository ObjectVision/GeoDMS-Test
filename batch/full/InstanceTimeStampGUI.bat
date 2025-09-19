Rem rapporteer de test, bepaal start en eind moment en voer de test uit

SETLOCAL EnableDelayedExpansion

Echo.
Echo ************************
Echo Test: %6

Call Full/SetStartTime.bat

Echo.
Echo Execute: %7  /%1 /%2 /%3 %4 %5 

Call %7 %1 %2 %3 %4 %5 %6

Call Full/SetEndTime.bat

Call Full/WriteTimeStamps.bat "%results_folder%\%6.txt"

