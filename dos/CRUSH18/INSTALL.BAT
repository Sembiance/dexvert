echo off
echo.
echo  INSTALL for CRUSH
if exist CRUSH.EXE goto go
echo  INSTALL must be run from the distribution disk or from
echo  a directory containing the distribution files.
goto exit
:go
if not "%1"=="" goto ok
echo.
echo  USAGE: INSTALL directory
echo.
echo  For example:
echo    INSTALL C:
echo    INSTALL \CRUSH1\
echo    INSTALL C:\UTILS\
echo.
echo ("directory" must end in ":" or "\" and must already exist)
echo.
goto exit
:ok
copy *.* %1*.*
:exit
