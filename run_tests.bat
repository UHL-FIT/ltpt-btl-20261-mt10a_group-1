@echo off
title Chay Kiem Thu (Unit Tests)
echo ========================================================
echo DANG CHAY KIEM THU TU DONG (UNIT TESTS)
echo ========================================================

:: Thu dung uv truoc
where uv >nul 2>&1
if %errorlevel% equ 0 (
    uv run python -m unittest discover -s tests -p "test_*.py" -v
) else (
    :: Fallback: dung venv
    if not exist ".venv\Scripts\activate.bat" (
        echo [LOI] Khong tim thay moi truong ao!
        echo Vui long chay setup_env.bat truoc.
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    python -m unittest discover -s tests -p "test_*.py" -v
)

echo ========================================================
pause
