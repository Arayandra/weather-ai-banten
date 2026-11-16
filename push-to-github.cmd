@echo off
setlocal EnableExtensions

REM Publish the complete extracted Weather AI project to the existing GitHub repo.
REM Add "." to SOURCE_DIR so the path does not end with a backslash inside quotes.
REM This prevents Robocopy from treating the closing quote as escaped on Windows.
set "SOURCE_DIR=%~dp0."
set "REPO_URL=https://github.com/Arayandra/weather-ai-banten.git"
set "WORK_DIR=%TEMP%\weather-ai-banten-publish-%RANDOM%-%RANDOM%"

 echo ============================================
 echo  Publish Weather AI Banten to GitHub
 echo ============================================

git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not available in PATH.
    pause
    exit /b 1
)

echo [1/4] Cloning the existing repository...
git clone "%REPO_URL%" "%WORK_DIR%"
if errorlevel 1 (
    echo ERROR: Could not clone the repository. Check internet access and GitHub sign-in.
    pause
    exit /b 1
)

echo [2/4] Copying the complete project into the cloned repository...
robocopy "%SOURCE_DIR%" "%WORK_DIR%" /E /R:2 /W:2 /XD .git .venv venv env __pycache__ /XF .env db.sqlite3 *.pyc
if errorlevel 8 goto :copy_failed

echo [3/4] Creating a commit...
git -C "%WORK_DIR%" add -A
git -C "%WORK_DIR%" diff --cached --quiet
if not errorlevel 1 (
    echo No new changes to upload.
    goto :push
)
git -C "%WORK_DIR%" commit -m "Upload complete Weather AI Banten project"
if errorlevel 1 (
    echo ERROR: Commit failed. Configure your Git user.name and user.email first.
    echo Run: git config --global user.name "Your Name"
    echo Run: git config --global user.email "you@example.com"
    pause
    exit /b 1
)

:push
echo [4/4] Pushing to GitHub...
git -C "%WORK_DIR%" push origin main
if errorlevel 1 (
    echo ERROR: Push failed. Check repository write access and GitHub authentication.
    pause
    exit /b 1
)

echo.
echo SUCCESS: Complete project pushed to %REPO_URL%
echo Temporary clone: %WORK_DIR%
pause
exit /b 0

:copy_failed
echo ERROR: Robocopy failed. The temporary clone is preserved at:
echo %WORK_DIR%
pause
exit /b 1
