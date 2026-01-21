@echo off
echo ========================================
echo Building Food Nutrition AI Agent...
echo ========================================

:: Check if pyinstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Build executable
echo.
echo Building executable...
pyinstaller --onefile --name "FoodAgent" --icon=NONE --console main.py

echo.
echo ========================================
echo Build complete!
echo Executable: dist\FoodAgent.exe
echo ========================================
echo.
echo NOTE: Copy .env file to dist\ folder before running!
echo Also copy knowledge_base\ folder to dist\ folder.
pause
