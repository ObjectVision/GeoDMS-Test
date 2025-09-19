Echo off

call unit_flagged.bat %1 S1 S2 S3
call unit_flagged.bat %1 S1 S2 C3
call unit_flagged.bat %1 S1 C2 S3
call unit_flagged.bat %1 S1 C2 C3

call unit_flagged.bat %1 C1 S2 S3
call unit_flagged.bat %1 C1 S2 C3
call unit_flagged.bat %1 C1 C2 S3
call unit_flagged.bat %1 C1 C2 C3
