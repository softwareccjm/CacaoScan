@echo off
echo ============================
echo Ejecutando tests con coverage para SonarQube
echo ============================

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Ejecutar pytest con coverage
python -m pytest --cov=. --cov-report=xml:coverage.xml --cov-report=term-missing -v

REM Verificar que se generó el archivo
if exist coverage.xml (
    echo.
    echo ============================
    echo coverage.xml generado exitosamente
    echo ============================
) else (
    echo.
    echo ERROR: coverage.xml NO SE GENERO
    exit /b 1
)

pause

