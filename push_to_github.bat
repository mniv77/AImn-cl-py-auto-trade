@echo off
cd /d "%~dp0"
git add .
git commit -m "Update project with latest changes"
git push -u origin main
pause