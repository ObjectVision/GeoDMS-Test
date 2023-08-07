REM Testen van Operatoren met verschillende Status Flags

SET GEODMS_DIRECTORIES_LOCALDATAPROJDIR=!LocalDataDirRegression!\operator

Call Full\InstanceTimeStamp.bat C1 C2 C3 %OperatorPath% results/regression/t010_operator_test/C1C2C3 t010_operator_test_C1C2C3
Call Full\InstanceTimeStamp.bat S1 C2 C3 %OperatorPath% results/regression/t010_operator_test/S1C2C3 t010_operator_test_S1C2C3
Call Full\InstanceTimeStamp.bat S1 S2 C3 %OperatorPath% results/regression/t010_operator_test/S1S2C3 t010_operator_test_S1S2C3
Call Full\InstanceTimeStamp.bat C1 S2 C3 %OperatorPath% results/regression/t010_operator_test/C1S2C3 t010_operator_test_C1S2C3

Call Full\InstanceTimeStamp.bat C1 C2 S3 %OperatorPath% results/regression/t010_operator_test/C1C2S3 t010_operator_test_C1C2S3
Call Full\InstanceTimeStamp.bat S1 C2 S3 %OperatorPath% results/regression/t010_operator_test/S1C2S3 t010_operator_test_S1C2S3
Call Full\InstanceTimeStamp.bat S1 S2 S3 %OperatorPath% results/regression/t010_operator_test/S1S2S3 t010_operator_test_S1S2S3
Call Full\InstanceTimeStamp.bat C1 S2 S3 %OperatorPath% results/regression/t010_operator_test/C1S2S3 t010_operator_test_C1S2S3

