Rem Schrijf de begin en eindmoment van de test weg naar de meegegeven test rsultaat file
Echo Write TimeStamps to "%~1"
Echo ************************

Echo ^<startdate^>%STARTDATETIME.YEAR%-%STARTDATETIME.MONTH%-%STARTDATETIME.DAY%^</startdate^>^<starttime^>%STARTDATETIME.HOUR%-%STARTDATETIME.MINUTE%-%STARTDATETIME.SECOND%^</starttime^>^<enddate^>%ENDDATETIME.YEAR%-%ENDDATETIME.MONTH%-%ENDDATETIME.DAY%^</enddate^>^<endtime^>%ENDDATETIME.HOUR%-%ENDDATETIME.MINUTE%-%ENDDATETIME.SECOND%^</endtime^> >> "%~1"


