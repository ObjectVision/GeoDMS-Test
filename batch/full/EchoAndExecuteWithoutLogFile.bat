Rem Show Command and Execute

Set command=%GeoDmsRunCmdBaseLarge% /%1 /%2 /%3 %4 %5 
Echo GeoDMS Command: %command%

%command% >> !tmpFileDir!\GeoDMSlog.txt

echo errorlevel: %errorlevel%
