REM JAR program to fully backup a drive to another drive
REM This program assumes that there is work space available on the hard drive
if "%1" == "" goto param_err
if "%2" == "" goto param_err
JAR16 a -r -b0 -vvas -w%1:\ -jt %2:\backup %1:\
goto end
:param_err
REM Usage: JARBACK hard_drive_letter diskette_drive_letter
REM        JARBACK C A
:end
