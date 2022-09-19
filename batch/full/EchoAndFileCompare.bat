Rem Show Command and CompareFile
Echo Execute: FC /b %1 %2 , write output to %3  

REM Echo FC %1 %2 > fc.txt

echo ^<br^> %4 ^:^ >> %3
FC /b %1 %2 > NUL && Echo Ok >> %3 || Echo False, difference(s) occur >> %3 
