@echo off
echo.
echo ---------------------------------------------------------------------
echo  TESTJAR.BAT - batch file to test the reliability of JAR
echo.
echo  This is a batch file to test the reliability of JAR compressing and
echo  decompressing your files on a specified drive. You can interrupt or
echo  shorten this test by pressing CTL BREAK. Please read documentation
echo  for more details about JAR testing.
echo.
echo  COMMAND SYNTAX:  testjar execute [drive_letter]
echo ---------------------------------------------------------------------
echo.

if NOT "%1" == "execute" goto end

if "%2" == "" goto no_drive

rem  ------ Drive letter specified ------

for %%i in (C c D d E e F f G g H h I i J j K k L l M m N n) do if "%%i" == "%2" goto driveok
for %%i in (O o P p Q q R r S s T t U u V v W w X x Y y Z z) do if "%%i" == "%2" goto driveok
goto bad_drive

:driveok
if EXIST testjar.$$$ del testjar.$$$

echo.
echo ------------------------------------
echo  Detecting locked files on drive %2:
echo ------------------------------------
echo.
echo on
JAR16 sl %2:\* -r -ltestjar.$$$ -ha -y
@echo off
if errorlevel 1 goto aborted
echo.
echo ------------------------------------
echo   Testing compression on drive %2:
echo ------------------------------------
echo.
echo on
JAR16 test archive %2:\* -m2 -r -jf -ho -x!testjar.$$$ -hbsh0
@echo off
if errorlevel 1 goto aborted
del testjar.$$$

echo.
echo ------------------------------------
echo  Detecting locked files on drive %2:
echo ------------------------------------
echo.
echo on
JAR32 sl %2:\* -r -ltestjar.$$$ -ha -y
@echo off
if errorlevel 1 goto aborted
echo.
echo ------------------------------------
echo   Testing compression on drive %2:
echo ------------------------------------
echo.
echo on
JAR32 test archive %2:\* -m2 -r -jf -ho -x!testjar.$$$ -hbsh0
@echo off
if errorlevel 1 goto aborted
del testjar.$$$
goto end

rem  ----- No drive letter specified ----

:no_drive
if EXIST testjar.$$$ del testjar.$$$

echo.
echo ------------------------------------
echo  Detecting locked files on drive C:
echo ------------------------------------
echo.
echo on
JAR16 sl C:\* -r -ltestjar.$$$ -ha -y
@echo off
if errorlevel 1 goto aborted
echo.
echo ------------------------------------
echo   Testing compression on drive C:
echo ------------------------------------
echo.
echo on
JAR16 test archive C:\* -m2 -r -jf -ho -x!testjar.$$$ -hbsh0
@echo off
if errorlevel 1 goto aborted
del testjar.$$$

echo.
echo ------------------------------------
echo  Detecting locked files on drive C:
echo ------------------------------------
echo.
echo on
JAR32 sl C:\* -r -ltestjar.$$$ -ha -y
@echo off
if errorlevel 1 goto aborted
echo.
echo ------------------------------------
echo   Testing compression on drive C:
echo ------------------------------------
echo.
echo on
JAR32 test archive C:\* -m2 -r -jf -ho -x!testjar.$$$ -hbsh0
@echo off
if errorlevel 1 goto aborted
del testjar.$$$
goto end

:bad_drive
echo.
echo ------------------------------------
echo   Incorrect drive letter specified
echo ------------------------------------
echo.
goto end

:aborted
if EXIST testjar.$$$ del testjar.$$$
echo.
echo ------------------------------------
echo          Testing aborted
echo ------------------------------------
echo.
pause

:end
