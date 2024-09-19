echo off
CLS
echo This is a quick demo of the operation of SLIM.
echo SLIM compresses files - all sorts of files -
echo to give you more free space on your disk.
echo And it automatically expands these files when accessed,
echo allowing you to use your files just as before.
echo.
PAUSE
CLS
echo Checking out drive A: before proceeding with demo.
COPY %0.BAT A:EXAMPLE.SLM
A:
IF EXIST SLIM.EXE GOTO PROCEED
echo The file SLIM.EXE should be on drive A: for this demo.
GOTO DEMOEND
:PROCEED
DEL EXAMPLE.SL1
COPY EXAMPLE.SLM EXAMPLE.SL1
IF EXIST EXAMPLE.SL1 GOTO PROCEED1
echo There is not enough free space on A:, or the disk is write protected.
GOTO DEMOEND
:PROCEED1
DEL EXAMPLE.SL1
echo.
echo O.K. Can proceed with demo.
PAUSE
CLS
SLIM ON
IF ERRORLEVEL 1 GOTO DEMOEND
echo.
echo SLIM is now RAM resident. This is needed to compress files
echo and to use them later. To compress a file is simple:
DIR *.SLM
echo.
echo SLIM will compress EXAMPLE.SLM as an example.
PAUSE
SLIM EXAMPLE.SLM
IF ERRORLEVEL 1 GOTO DEMOEND
echo.
PAUSE
CLS
echo To use the compressed file is even simpler.
echo If SLIM is RAM resident and active (SLIM ON),
echo and enough disk space is free to hold the un-compressed file,
echo SLIM automatically expands the file when accessed,
echo allowing it to be used just as before. You could TYPE the
echo file, for instance.
PAUSE
TYPE EXAMPLE.SLM



PAUSE
CLS
echo For backup, copying, etc., SLIM may be turned OFF. This allows
echo a compressed file to be accessed without automatic expansion.
echo Type SLIM OFF to do this and you can then copy or display compressed
echo files, or manipulate them in any other way. For example:
echo.
echo SLIM OFF
SLIM OFF
echo.
echo.
echo COPY EXAMPLE.SLM EXAMPLE.SL1
COPY EXAMPLE.SLM EXAMPLE.SL1
echo.
echo DIR EXAMPLE.SL?
DIR EXAMPLE.SL?
PAUSE
CLS
echo Do not try to use a compressed file when SLIM is OFF,
echo or before SLIM is loaded by the first SLIM ON command.
echo The file will not then make sense - but look something 
echo like this...
echo.
TYPE EXAMPLE.SLM
echo.
echo.
PAUSE
CLS
echo To see which files are compressed by SLIM and by how much,
echo use the SLIM R command, eg SLIM R EXAMPLE.*
SLIM R EXAMPLE.*
echo.
PAUSE
CLS
echo Compressed files may be de-compressed by the SLIM X command.
echo eg SLIM X EXAMPLE.SLM
echo.
SLIM X EXAMPLE.SLM
echo.
echo.
DIR EXAMPLE.SLM
PAUSE
DEL EXAMPLE.SLM
DEL EXAMPLE.SL1
CLS
echo For a quick reference to SLIM commands, just type SLIM.
PAUSE
echo.
SLIM
echo.
:DEMOEND
echo This concludes the demonstration.
