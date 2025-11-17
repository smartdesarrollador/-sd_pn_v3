@echo off
REM Build script for Widget Sidebar
REM Compiles the application to a standalone .exe using PyInstaller

echo ============================================================
echo Widget Sidebar - Build Script
echo ============================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Step 1: Create backup of JSON files
echo Creating backup of JSON configuration files...
if exist config.json (
    copy config.json config.json.backup >nul 2>&1
    echo   - config.json.backup created
)
if exist default_categories.json (
    copy default_categories.json default_categories.json.backup >nul 2>&1
    echo   - default_categories.json.backup created
)
echo.

REM Step 2: Run migration to SQLite
echo Running migration from JSON to SQLite...
python run_migration.py >nul 2>&1
if errorlevel 1 (
    echo   WARNING: Migration may have failed, but continuing build...
) else (
    echo   - Migration completed successfully
)
echo.

echo Starting PyInstaller build...
pyinstaller widget_sidebar.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Build FAILED
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo Copying additional files to dist...

REM Copy database to dist folder
if exist widget_sidebar.db (
    copy widget_sidebar.db dist\ >nul 2>&1
    echo   - widget_sidebar.db copied to dist
)

REM Copy README and documentation to dist folder
if exist USER_GUIDE.md (
    copy USER_GUIDE.md dist\ >nul 2>&1
    echo   - USER_GUIDE.md copied to dist
)
if exist README.md (
    copy README.md dist\ >nul 2>&1
    echo   - README.md copied to dist
)
if exist LICENSE (
    copy LICENSE dist\ >nul 2>&1
    echo   - LICENSE copied to dist
)

REM Create distribution folder with version
echo.
echo Creating distribution package...
set VERSION=2.0
if not exist "WidgetSidebar_v%VERSION%" mkdir "WidgetSidebar_v%VERSION%"
xcopy /E /I /Y dist "WidgetSidebar_v%VERSION%" >nul 2>&1
echo   - Distribution package created: WidgetSidebar_v%VERSION%\

echo.
echo ============================================================
echo Build SUCCESSFUL
echo ============================================================
echo.
echo Executable location: dist\WidgetSidebar.exe
echo Distribution package: WidgetSidebar_v%VERSION%\
echo.
echo You can now run the application by executing:
echo   dist\WidgetSidebar.exe
echo.
echo Or distribute the WidgetSidebar_v%VERSION% folder
echo.
pause
