REM JAR program to incrementally backup one drive to another drive
REM This program assumes that there is work space available on the hard drive
if "%1" == "" goto param_err
if "%2" == "" goto param_err
JAR16 a -r -vvas -b0 -hba1 -w%1:\ -jt %2:\backup %1:\
goto end
:param_err
REM Usage: JARINCR hard_drive_letter diskette_drive_letter
REM        JARINCR C A
:end
