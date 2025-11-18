@echo off
:: Wrapper para executar o PowerShell com privilégios elevados
powershell -ExecutionPolicy Bypass -File "%~dp0RollbackHelper.ps1"
pause