if (%1) EQU () (
	echo ERROR: No version specified.
	pause
	exit /b 1
)
call full %1 S1 S2 C3 QUIET
call full %1 S1 C2 S3 QUIET
call full %1 S1 C2 C3 QUIET
call full %1 C1 S2 S3 QUIET
call full %1 C1 S2 C3 QUIET
call full %1 C1 C2 S3 QUIET
call full %1 C1 C2 C3 QUIET
call full %1 S1 S2 S3 QUIET
