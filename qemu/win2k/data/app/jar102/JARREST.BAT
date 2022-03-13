REM JAR program to restore archives on a drive to another drive overwriting
if "%1" == "" goto param_err
if "%2" == "" goto param_err
JAR16 x -y %1:backup -o%2:\
goto end
:param_err
REM Usage: JARREST diskette_drive_letter hard_drive_letter
REM        JARREST A C
:end
