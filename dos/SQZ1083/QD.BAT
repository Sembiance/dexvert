@echo off
:MAIN
shift
if "%0" == "" goto END
sqz u %0 /WSp1q0z1 %0\*.*
if errorlevel 128 goto L_NOT_AN_ERROR
if errorlevel 1 goto ERROR
:L_NOT_AN_ERROR
sqz t %0 /Wz1
if errorlevel 128 goto L_REMOVE
if errorlevel 1 goto ERROR
:L_REMOVE
ncd RMTREE /BATCH %0
if errorlevel 1 goto ERROR
goto MAIN
:ERROR
echo ERROR from SQZ while packing %0
:END
