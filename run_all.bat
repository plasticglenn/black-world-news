@echo off
REM ============================================================
REM  Full pipeline — runs the AI agent, picks a featured story,
REM  rebuilds the site, and publishes. Scheduled every 2 days.
REM  (The daily featured rotation is shuffle_daily.bat.)
REM ============================================================
cd /d C:\Users\glenn\dispatch-agent
set PYTHONIOENCODING=utf-8

echo Running news agent...
python dispatch.py --all

echo Picking featured story...
python pick_featured.py

echo Generating site...
python generate_site.py

echo Publishing...
git add -A
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Auto-update: fresh stories + featured"
  git push origin main
  echo Done.
) else (
  echo Nothing to publish.
)
