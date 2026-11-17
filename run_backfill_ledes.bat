@echo off
REM Fetch each story's first line, then rebuild the site (does not publish).
cd /d C:\Users\glenn\dispatch-agent
set PYTHONIOENCODING=utf-8
python backfill_ledes.py
python generate_site.py
echo.
echo Finished. You can close this window.
pause
