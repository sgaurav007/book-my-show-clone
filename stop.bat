@echo off
REM BookMyShow Clone - Stop Script for Windows

echo.
echo ================================================
echo   Stopping BookMyShow Clone
echo ================================================
echo.

set /p REMOVE_VOLUMES="Remove volumes (wipe databases)? (y/n): "

if /i "%REMOVE_VOLUMES%"=="y" (
    echo Stopping all services and removing volumes...
    docker-compose down -v
    echo [OK] All services stopped and data removed
) else (
    echo Stopping all services (keeping data)...
    docker-compose down
    echo [OK] All services stopped (data preserved)
)

echo.
echo To start again, run: start.bat
echo.
pause
