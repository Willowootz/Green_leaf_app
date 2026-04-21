@echo off
title Python Dependencies
echo ----------------------------------------------
echo Installing Python Packages...
echo ----------------------------------------------

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b
)

::pip upgrade
echo [1/3] Upgrading pip...
python -m pip install --upgrade pip

::install
echo [2/3] Installing pandas, requests, toml, Flask, flask-cors, and scikit-learn...
pip install pandas requests toml Flask flask-cors scikit-learn

::verify
echo [3/3] Verifying installation...
pip show pandas requests toml Flask flask-cors scikit-learn | findstr "Name Version"

echo ----------------------------------------------
echo Installation Complete
echo ----------------------------------------------
pause