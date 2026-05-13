@echo off
echo ========================================================
echo KHOI TAO MOI TRUONG PHAT TRIEN (UV SYNC)
echo ========================================================

:: Kiem tra uv da cai chua
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Chua cai dat UV. Dang thu cai dat...
    pip install uv
    if %errorlevel% neq 0 (
        echo [FALLBACK] Dung pip + venv thay the...
        goto :PIP_FALLBACK
    )
)

echo [1/2] Dang dong bo moi truong voi UV...
uv sync
echo [2/2] Hoan tat!

echo.
echo ========================================================
echo HOAN TAT! De chay ung dung:
echo   uv run python main.py
echo ========================================================
pause
goto :EOF

:PIP_FALLBACK
echo [1/3] Dang tao moi truong ao .venv...
IF NOT EXIST ".venv" (
    python -m venv .venv
) ELSE (
    echo .venv da ton tai.
)

echo [2/3] Kich hoat moi truong...
call .venv\Scripts\activate.bat

echo [3/3] Cai dat thu vien...
pip install -r requirements.txt

echo.
echo ========================================================
echo HOAN TAT! De chay ung dung:
echo   .venv\Scripts\activate
echo   python main.py
echo ========================================================
pause
