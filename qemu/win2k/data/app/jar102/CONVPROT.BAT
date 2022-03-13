@if "%1"=="" goto syntax
@if "%2"=="" goto syntax
@echo.
@echo ----- Unprotecting archive -----
JAR16 y %1 -g%2 -jg -jt
@if errorlevel 1 goto abort
@echo ----- Protecting archive using "Authenticate" method -----
JAR16 y %1 -jg%2 -hg"Authenticate" -jt
@if errorlevel 1 goto abort
@echo ----- Archive sucessfully protected using "Authenticate" method -----
@goto end

:syntax
@echo.
@echo -----------------------------------------------------------------
@echo   Usage: convprot {archive} {password}
@echo   Batch file first unprotects passworded archive and then
@echo   protects it using the same password and "Authenticate" method
@echo -----------------------------------------------------------------
@echo.
@goto end

:abort
@echo.
@echo -------------------------------------
@echo   JAR returned non-zero error level
@echo   Batch file aborted
@echo -------------------------------------
@echo.
@pause
@goto end

:end
