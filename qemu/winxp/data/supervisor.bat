@echo off

:waitForService
for /F "tokens=3 delims=: " %%H in ('sc query "LanmanServer" ^| findstr "        STATE"') do (
	if /I "%%H" NEQ "RUNNING" (
		ping localhost -n 2 > NUL
		goto waitForService
	)
)

net share in=c:\in /UNLIMITED
net share out=c:\out /UNLIMITED

start "c:\Program Files\AutoIt3\AutoIt3.exe" c:\dexvert\supervisor.au3
