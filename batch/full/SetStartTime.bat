Rem Bepaal het startmoment van de test en geeft dit weer

set STD=
for /f "skip=1 delims=" %%x in ('wmic os get localdatetime') do if not defined STD set STD=%%x
set STARTDATETIME.YEAR=%STD:~0,4%
set STARTDATETIME.MONTH=%STD:~4,2%
set STARTDATETIME.DAY=%STD:~6,2%
set STARTDATETIME.HOUR=%STD:~8,2%
set STARTDATETIME.MINUTE=%STD:~10,2%
set STARTDATETIME.SECOND=%STD:~12,2%

Echo.
Echo Start date time: %STARTDATETIME.YEAR%-%STARTDATETIME.MONTH%-%STARTDATETIME.DAY% %STARTDATETIME.HOUR%:%STARTDATETIME.MINUTE%:%STARTDATETIME.SECOND%

