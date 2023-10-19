REM Maak Rapport

Set GeoDMSReportBaseFolder=%TstDir%\Regression\GeoDMSTestResults

Echo.
Echo ************************
Echo Make Report
Echo.
Echo Maak bestand met uitgevoerde testen via commando: 
Echo Dir %GeoDMSReportBaseFolder%\*.txt to %tmpFileDir%\dirinfo.str /S /B /O

Dir %GeoDMSReportBaseFolder%\*.txt > %tmpFileDir%\dirinfo.str /S /B /O

Echo.
Echo Maak HTML Rapportage met commando: %GeoDmsRunCmdBaseLarge% %RegressionPath% mergeToRapport/total/Export

%GeoDmsRunCmdBaseLarge% %RegressionPath% mergeToRapport/total/Export >> !tmpFileDir!\GeoDMSlog.txt

Echo.
Echo ************************

set /p ver_range=<%tmpFileDir%/temp_ver_range.txt

set GeoDMSReportFile=%GeoDMSReportBaseFolder%\reports\!ver_range!.html

REM Echo Removing CalcCache files %LocalDataDirRegression%\*.dmsdata
REM Del /S %LocalDataDirRegression%\*.dmsdata 2>nul

Echo.
Echo ************************
Echo Results written to: %GeoDMSReportFile%
Echo GeoDMS Log file written to: %tmpFileDir%\GeoDMSlog.txt
Echo ************************
Echo.

start %GeoDMSReportFile%