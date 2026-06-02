@echo off
REM ============================================================
REM  Daily "shuffle the deck" — rotate the featured story and
REM  refresh the homepage. NO AI agent, so it costs nothing.
REM  The agent (run_all.bat) runs every 2 days; this runs daily.
REM ============================================================
cd /d C:\Users\glenn\dispatch-agent
set PYTHONIOENCODING=utf-8

echo Rotating featured story...
python pick_featured.py

echo Rebuilding site...
python generate_site.py

echo Publishing...
git add -A
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Daily refresh: rotate featured story"
  git push origin main
  echo Published.
) else (
  echo No changes to publish.
)
