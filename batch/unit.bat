Echo off

REM %1 = version selector (D32/R32/D64/R64/CD64/CR64 dev-tree shortcut,
REM      OR a numeric version like 20.0.0 to point at an installed build).
REM %2 = flavor suffix (m / c / l) appended to the installed dir name.
REM      Required when %1 is a numeric version; ignored for dev-tree
REM      shortcuts. Empty / omitted is tolerated but won't find an
REM      installed build whose dir is GeoDms<ver>.<flavor>.

call unit_flagged.bat %1 %2 S1 S2 S3
REM call unit_flagged.bat %1 %2 S1 S2 C3
REM call unit_flagged.bat %1 %2 S1 C2 S3
REM call unit_flagged.bat %1 %2 S1 C2 C3

REM call unit_flagged.bat %1 %2 C1 S2 S3
REM call unit_flagged.bat %1 %2 C1 S2 C3
REM call unit_flagged.bat %1 %2 C1 C2 S3
REM call unit_flagged.bat %1 %2 C1 C2 C3
