@echo off
REM ====================================================================
REM Regenerate Psychology Dataset — N worker song song qua DeepSeek
REM ====================================================================
REM Yeu cau:
REM   1. ds2api dang chay tren http://localhost:5001/v1
REM   2. set DEEPSEEK_API_KEY=my-secret-key-12345
REM   3. set DEEPSEEK_BASE_URL=http://localhost:5001/v1
REM
REM Cach dung:
REM   scripts\regenerate_psych_parallel.bat                  → 3 worker x 500 = 1500
REM   scripts\regenerate_psych_parallel.bat 500 3            → 3 worker x 500
REM   scripts\regenerate_psych_parallel.bat 300 5            → 5 worker x 300
REM ====================================================================

setlocal EnableDelayedExpansion

set TARGET_PER_WORKER=%1
if "%TARGET_PER_WORKER%"=="" set TARGET_PER_WORKER=500

set NUM_WORKERS=%2
if "%NUM_WORKERS%"=="" set NUM_WORKERS=3

set BATCH=3
set MODEL=deepseek-v4-flash-nothinking

if "%DEEPSEEK_API_KEY%"=="" (
    echo [ERROR] DEEPSEEK_API_KEY chua set. Chay truoc:
    echo   set DEEPSEEK_API_KEY=my-secret-key-12345
    echo   set DEEPSEEK_BASE_URL=http://localhost:5001/v1
    exit /b 1
)

if "%DEEPSEEK_BASE_URL%"=="" (
    echo [WARN] DEEPSEEK_BASE_URL chua set. Mac dinh: http://localhost:5001/v1
    set DEEPSEEK_BASE_URL=http://localhost:5001/v1
)

set /a TOTAL = %TARGET_PER_WORKER% * %NUM_WORKERS%

echo ====================================================================
echo Launching %NUM_WORKERS% workers in parallel
echo   Target per worker : %TARGET_PER_WORKER%
echo   Total target      : %TOTAL%
echo   Batch size        : %BATCH%
echo   Model             : %MODEL%
echo   Base URL          : %DEEPSEEK_BASE_URL%
echo ====================================================================
echo.

set /a LAST = %NUM_WORKERS% - 1
for /L %%I in (0,1,%LAST%) do (
    echo   Launching worker %%I ...
    start "PsychWorker-%%I" cmd /k python scripts\regenerate_psychology_data.py ^
        --target %TARGET_PER_WORKER% ^
        --batch %BATCH% ^
        --model %MODEL% ^
        --worker-id %%I
)

echo.
echo Da launch %NUM_WORKERS% workers. Theo doi progress trong tung cua so.
echo.
echo SAU KHI TAT CA WORKER XONG, chay lenh sau de gop ket qua:
echo   python scripts\regenerate_psychology_data.py --merge %NUM_WORKERS%
echo.

endlocal
