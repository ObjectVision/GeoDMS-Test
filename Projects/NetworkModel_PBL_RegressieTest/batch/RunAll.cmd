set geodmsversion=GeoDms15.1.0
set exe_dir=C:\Program Files\ObjectVision\%geodmsversion%
set ProgramPath=%exe_dir%\GeoDmsRun.exe

cd ..\cfg

REM CHOICE /M "Wil je eerder gemaakte ontkoppelde OSM data hergebruiken en dus draaien van maak OSM-data overslaan?"
REM if ErrorLevel 2 goto runPrepareData
REM CHOICE /M "Wil je eerder gemaakte ontkoppelde congestion data hergebruiken en dus draaien van het congestions speed netwerk overslaan? Dit is de stap die zoveel tijd kost."
REM if ErrorLevel 2 goto runCongestionData
REM GOTO runDayGroups

:runPrepareData
REM "%ProgramPath%" main.dms /MaakOntkoppeldeData/OSM/Step1_Generate_roads_shp2fss REM ruwe OSM naar fss
REM call ..\batch\RunPrepare.cmd MonTue                                            REM maak finale OSM netwerk per dag groep
REM call ..\batch\RunPrepare.cmd WedThuFri 
REM call ..\batch\RunPrepare.cmd SatSun 

:runCongestionData
REM call ..\batch\RunCongestionSpeeds.cmd MonTue 
REM call ..\batch\RunCongestionSpeeds.cmd WedThuFri 
REM call ..\batch\RunCongestionSpeeds.cmd SatSun 

:runDayGroups
REM call ..\batch\RunDayGroups.cmd MonTue 
REM call ..\batch\RunDayGroups.cmd WedThuFri 
REM call ..\batch\RunDayGroups.cmd SatSun 

:runPublicTransport
set Orgset_EnkeleCorop_selectie=Delfzijl_en_omgeving
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Oost_Groningen
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Delfzijl_en_omgeving
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Overig_Groningen
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Noord_Friesland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidwest_Friesland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidoost_Friesland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Noord_Drenthe
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidoost_Drenthe
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidwest_Drenthe
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Noord_Overijssel
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidwest_Overijssel
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Twente
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Veluwe
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Achterhoek
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Arnhem_Nijmegen
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidwest_Gelderland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Utrecht
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Kop_van_Noord_Holland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Alkmaar_en_omgeving
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=IJmond
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Agglomeratie_Haarlem
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zaanstreek
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Groot_Amsterdam
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Het_Gooi_en_Vechtstreek
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Agglomeratie_Leiden_en_Bollenstreek
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Agglomeratie_s_Gravenhage
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Delft_en_Westland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Oost_Zuid_Holland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Groot_Rijnmond
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidoost_Zuid_Holland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zeeuwsch_Vlaanderen
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Overig_Zeeland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=West_Noord_Brabant
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Midden_Noord_Brabant
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Noordoost_Noord_Brabant
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuidoost_Noord_Brabant
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Noord_Limburg
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Midden_Limburg
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Zuid_Limburg
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles
set Orgset_EnkeleCorop_selectie=Flevoland
"%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PublicTransport/Generate_Output/OUTPUT_Generate_fullOD_long_CSVFiles




pause "Klaar ?"