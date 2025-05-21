REM Testen van Operatoren met verschillende Status Flags

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\operator

Call Full\InstanceTimeStamp.bat %Setting1% %Setting2% %Setting3% %OperatorPath% results/regression/t010_operator_test/stored_result t010_operator_test

