@echo off
:MAIN
shift
if "%0" == "" goto END
sqz u %0 /WSp1q0z1 %0\*.*
if errorlevel 128 goto MAIN
if errorlevel 1 goto ERROR
goto MAIN
:ERROR
echo ERROR from SQZ while packing %0
:END
