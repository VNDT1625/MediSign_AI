@echo off
echo Starting Hello Bacsi crawler with auto-restart...
echo Press Ctrl+C to stop manually.
echo.

:loop
echo [%date% %time%] Running crawler...
python scripts\crawl_hellobacsi.py --max-pages 99999
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% EQU 0 (
    echo [%date% %time%] Crawl completed successfully.
    goto done
)

echo [%date% %time%] Crawler exited with code %EXIT_CODE%. Restarting in 10 seconds...
timeout /t 10 /nobreak > nul
goto loop

:done
echo All done.
pause
