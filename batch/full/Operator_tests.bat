REM Testen van Operatoren met verschillende Status Flags

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\operator

Call Full\InstanceTimeStamp.bat C1 C2 %OperatorPath% results/regression/t010_operator_test/C1C2 t010_operator_test_C1C2
Call Full\InstanceTimeStamp.bat S1 C2 %OperatorPath% results/regression/t010_operator_test/S1C2 t010_operator_test_S1C2
Call Full\InstanceTimeStamp.bat S1 S2 %OperatorPath% results/regression/t010_operator_test/S1S2 t010_operator_test_S1S2
Call Full\InstanceTimeStamp.bat C1 S2 %OperatorPath% results/regression/t010_operator_test/C1S2 t010_operator_test_C1S2
