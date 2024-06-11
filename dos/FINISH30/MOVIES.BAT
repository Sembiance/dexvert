cls
@echo off
@echo   MOVIES TO GO!    MASTER Disk Batch File
@md a
@echo ÿ
@copy read.me %1\
@copy install.fil %1\
@copy c:\util\install.exe %1\
@stamp %1\*.* 01-01-1994 12:00:00
@echo ÿ
@echo   Making SCRIPT.PAK  . . .
@copy part2.fil a
@cd a
@stamp *.* 01-01-1994 12:00:00
@pack_r %1\script.pak *.* /o
@del *.fil
@cd ..
@echo ÿ
@echo ÿ
@echo       Making DATA.PAK  . . .
@copy ..\1a.fil a
@copy ..\2a.fil a
@copy ..\3a.fil a
@copy ..\4a.fil a
@cd a
@stamp *.* 01-01-1994 12:00:00
@pack_r %1\data.pak *.* /o
@del *.fil
@cd ..
@echo ÿ
@echo       Making TEXT.PAK  . . .
@copy ..\text.exe a
@copy ..\submit.txt a
@copy ..\order.txt a
@cd a
@stamp *.* 01-01-1994 12:00:00
@pack_r %1\text.pak *.* /o
@del *.exe
@del *.txt
@cd ..
@echo ÿ
@echo       Making GRAPHICS.PAK . . .
@copy ..\movies.exe a
@copy ..\helv.sf a
@copy ..\icon.wl a
@copy ..\movie.wl a
@copy ..\movie.ml a
@copy ..\movies.ico a
@copy ..\movies.pif a
@copy ..\movie.hlp a
@copy ..\reviewer.wl a
@cd a
@stamp *.* 01-01-1994 12:00:00
@pack_r %1\graphics.pak *.* /o
@del *.exe
@del *.wl
@del *.ml
@del *.sf
@del *.ico
@del *.pif
@del *.hlp
@cd ..
@echo ÿ
@echo       Making ICON.PAK . . .
@copy ..\actor.wl a
@copy ..\actor.ml a
@copy ..\poster.wl a
@copy ..\poster.ml a
@copy ..\demo.* a
@copy ..\cat*.wl a
@copy ..\f*.wl a
@copy ..\search*.wl a
@copy ..\icon.ml a
@cd a
@stamp *.* 01-01-1994 12:00:00
@pack_r %1\icon.pak *.* /o
@del *.wl
@del *.ml
@cd ..
@echo ÿ
@echo       Making WINDOWS.PAK . . .
@copy ..\*.pif a
@copy ..\*.ico a
@copy ..\*.grp a
@cd a
@stamp *.* 01-01-1994 12:00:00
@pack_r %1\windows.pak *.* /o
@del *.ico
@del *.pif
@del *.grp
@cd ..
@rd a
@stamp %1\*.* 01-01-1994 12:00:00
