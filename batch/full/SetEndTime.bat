Rem Bepaal het eindmoment van de test

set ETD=
for /f "skip=1 delims=" %%x in ('wmic os get localdatetime') do if not defined ETD set ETD=%%x
set ENDDATETIME.YEAR=%ETD:~0,4%
set ENDDATETIME.MONTH=%ETD:~4,2%
set ENDDATETIME.DAY=%ETD:~6,2%
set ENDDATETIME.HOUR=%ETD:~8,2%
set ENDDATETIME.MINUTE=%ETD:~10,2%
set ENDDATETIME.SECOND=%ETD:~12,2%

Echo.
Echo End date time: %ENDDATETIME.YEAR%-%ENDDATETIME.MONTH%-%ENDDATETIME.DAY% %ENDDATETIME.HOUR%:%ENDDATETIME.MINUTE%:%ENDDATETIME.SECOND%


