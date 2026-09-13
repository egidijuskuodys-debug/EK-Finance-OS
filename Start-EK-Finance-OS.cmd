@echo off
setlocal

title EK Finance OS Launcher

set "PROJECT_DIR=%~dp0"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"
set "APP_URL=http://localhost:5173/dashboard"

set "DOCKER_USER=%LocalAppData%\Programs\DockerDesktop\frontend\Docker Desktop.exe"
set "DOCKER_SYSTEM=%ProgramFiles%\Docker\Docker\Docker Desktop.exe"

cd /d "%PROJECT_DIR%"

echo.
echo Starting EK Finance OS...
echo.

docker info >nul 2>&1

if errorlevel 1 (
    echo Docker Desktop is not running.

    if exist "%DOCKER_USER%" (
        echo Starting Docker Desktop...
        start "" "%DOCKER_USER%"
        goto wait_for_docker
    )

    if exist "%DOCKER_SYSTEM%" (
        echo Starting Docker Desktop...
        start "" "%DOCKER_SYSTEM%"
        goto wait_for_docker
    )

    echo Docker Desktop was not found.
    echo Start Docker Desktop manually and try again.
    pause
    exit /b 1
)

goto docker_ready


:wait_for_docker

echo Waiting for Docker...

for /l %%i in (1,1,90) do (
    docker info >nul 2>&1

    if not errorlevel 1 (
        goto docker_ready
    )

    timeout /t 2 /nobreak >nul
)

echo Docker did not start in time.
pause
exit /b 1


:docker_ready

echo Starting database and backend...
docker compose up -d

if errorlevel 1 (
    echo Failed to start Docker services.
    pause
    exit /b 1
)

echo Waiting for backend...

for /l %%i in (1,1,60) do (
    curl.exe -s -o NUL http://localhost:8000/health

    if not errorlevel 1 (
        goto backend_ready
    )

    timeout /t 1 /nobreak >nul
)

echo Backend did not start in time.
pause
exit /b 1


:backend_ready

netstat -ano | findstr /R /C:":5173 .*LISTENING" >nul

if errorlevel 1 (
    echo Starting frontend...

    start "EK Finance OS Frontend" cmd.exe /k "cd /d ""%FRONTEND_DIR%"" && npm.cmd run dev"
) else (
    echo Frontend is already running.
)

echo Waiting for frontend...

for /l %%i in (1,1,60) do (
    curl.exe -s -o NUL http://localhost:5173/

    if not errorlevel 1 (
        goto frontend_ready
    )

    timeout /t 1 /nobreak >nul
)

echo Frontend did not start in time.
pause
exit /b 1


:frontend_ready

echo Opening EK Finance OS...
start "" "%APP_URL%"

echo.
echo EK Finance OS is ready.
timeout /t 2 /nobreak >nul

endlocal
exit /b 0