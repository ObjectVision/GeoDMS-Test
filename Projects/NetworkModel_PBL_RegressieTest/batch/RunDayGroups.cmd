set DAYGROUP=%1
 "%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/Generate_Output/OUTPUT_Generate_PublicTransport_fullOD_long_CSVFiles
 "%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/Generate_Output/OUTPUT_Generate_Car_traveltimes_CSVFiles
 "%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/Generate_Output/OUTPUT_Generate_Bike_traveltimes_CSVFiles
 "%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/Generate_Output/OUTPUT_Generate_Pedestrian_traveltimes_CSVFiles

REM "%ProgramPath%" main.dms /NetworkSetup/ConfigurationPerRegio/all/PrivateTransport/Car/ExportTable_Traveltimes/File
