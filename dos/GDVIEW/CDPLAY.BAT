@echo off
if A%1A == AA goto noparam
gdv %1 -cdda
goto end
:noparam
gdv -cdplay
:end
