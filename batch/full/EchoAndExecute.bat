Rem Show Command and Execute

Echo GeoDMS Command: %GeoDmsRunCmdBaseLarge% /%1 /%2 /%3 %4 %5 

%GeoDmsRunCmdBaseLarge% /%1 /%2 /%3 %4 %5 >> !LogFileDir!\GeoDMSlog.txt

echo %errorlevel%
