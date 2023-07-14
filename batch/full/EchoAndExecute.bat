Rem Show Command and Execute

 Echo GeoDMS Command: %GeoDmsRunCmdBaseLarge% /%1 /%2 %3 %4 
REM  Echo GeoDMS Command: %GeoDmsRunCmdBaseLarge% %3 %4 

%GeoDmsRunCmdBaseLarge% /%1 /%2 %3 %4 >> !LogFileDir!\GeoDMSlog.txt
echo %errorlevel%
REM %GeoDmsRunCmdBaseLarge% %3 %4 >> !LogFileDir!\GeoDMSlog.txt