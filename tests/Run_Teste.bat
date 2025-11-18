@echo off
echo ===============================================
echo  TESTES - Editor Foto 3x4
echo ===============================================
set "ROOT_DIR=%~dp0.."
cd /d "%ROOT_DIR%"
py -m pytest tests/ -v --tb=short

if exist ".pytest_cache" rd /s /q ".pytest_cache" 2>nul
if exist "__pycache__" rd /s /q "__pycache__" 2>nul
if exist "tests\__pycache__" rd /s /q "tests\__pycache__" 2>nul
if exist "tests\.pytest_cache" rd /s /q "tests\.pytest_cache" 2>nul
PAUSE

