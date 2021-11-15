echo off
cls
echo ÿ
echo This Batch file will print the Outline! documentation file MANUAL.DOC
echo to printer port LPT1:.
echo ÿ
echo Press any key to begin (^Break to Abort)
echo ÿ
pause
echo ÿ
echo      Now printing . . . .
copy manual.doc lpt1:
echo ÿ
echo      Printing complete
echo ÿ

