Echo off

REM %1 = version selector (D32/R32/D64/R64/CD64/CR64/GD64/GR64 dev-tree shortcut,
REM      OR a numeric version like 20.0.0 to point at an installed build).
REM %2 = flavor suffix (m / c / g / l) appended to the installed dir name.
REM      Required when %1 is a numeric version; with a dev-tree shortcut it
REM      only reaches the tests as GeoDmsFlavor (pass g with GD64/GR64).
REM      Empty / omitted is tolerated but won't find an installed build
REM      whose dir is GeoDms<ver>.<flavor>.

call unit_flagged.bat %1 %2 S1 S2 S3
REM call unit_flagged.bat %1 %2 S1 S2 C3
REM call unit_flagged.bat %1 %2 S1 C2 S3
REM call unit_flagged.bat %1 %2 S1 C2 C3

REM call unit_flagged.bat %1 %2 C1 S2 S3
REM call unit_flagged.bat %1 %2 C1 S2 C3
REM call unit_flagged.bat %1 %2 C1 C2 S3
REM call unit_flagged.bat %1 %2 C1 C2 C3
