@echo off
echo ========================================================
echo DANG DON DEP CAC FILE RAC...
echo ========================================================

if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
if exist "PatientManagement.spec" del "PatientManagement.spec"

echo Xoa __pycache__ va .pyc...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo Xoa file log...
if exist "data\app.log" del "data\app.log"

echo ========================================================
echo HOAN TAT DON DEP!
echo ========================================================
pause
