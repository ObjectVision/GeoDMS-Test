REM Remark: SourceDataDir in options menu of the GUI, tab 'general settings'is leading for localisation of the SourceData.
REM GeoDmsRun.exe [/PProjName] [/LLogFileName] ConfigFileName ItemNames
REM [] means optional
REM Close GUI-variant(GeoDmsGui.exe) if running GeoDmsRun.exe (if this is the same)
REM Results are saved in: ../LD/%configname%/results/...
REM When running again, files are simply overwritten

Call path/set.bat

Call country.bat
Call Start.bat

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

Call SSP1.bat
"%exe_path%" /L"%log_dir%\CombinationUrbNotUrbOccurring_SSP1.txt" "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Analysis_Modelled/UrbanDif2010_2100_steps/export_csv/Result

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

Call SSP2.bat
"%exe_path%" /L"%log_dir%\CombinationUrbNotUrbOccurring_SSP2.txt" "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP2/Analysis_Modelled/UrbanDif2010_2100_steps/export_csv/Result

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

Call SSP3.bat
"%exe_path%" /L"%log_dir%\CombinationUrbNotUrbOccurring_SSP3.txt" "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP3/Analysis_Modelled/UrbanDif2010_2100_steps/export_csv/Result

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

Call SSP4.bat
"%exe_path%" /L"%log_dir%\CombinationUrbNotUrbOccurring_SSP4.txt" "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP4/Analysis_Modelled/UrbanDif2010_2100_steps/export_csv/Result

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

Call SSP5.bat
"%exe_path%" /L"%log_dir%\CombinationUrbNotUrbOccurring_SSP5.txt" "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP5/Analysis_Modelled/UrbanDif2010_2100_steps/export_csv/Result

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

"%exe_path%" /L"%log_dir%\exportmetadata.txt" "%prj_dir%\cfg\stam.dms" /Scenarios/exportmetadata

Call Start_Past.bat

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

Call SSPPast_tif.bat

del K:\LD\towardsanurbanpreview\CalcCachex64.v7.315\*.* /S /F /Q
rmdir /S /Q K:\LD\towardsanurbanpreview\CalcCachex64.v7.315

Call validation.bat

REM Call SSPclaim_generator.bat



