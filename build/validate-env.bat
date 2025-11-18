@echo off
echo Validando ambiente de build...
dotnet --version >nul 2>&1 || (echo [X] ERRO: .NET SDK ausente & exit /b 1)
py --version >nul 2>&1 || (echo [X] ERRO: Python ausente & exit /b 1)
pip show pillow >nul 2>&1 || (echo [X] ERRO: Pillow ausente & exit /b 1)
pip show customtkinter >nul 2>&1 || (echo [X] ERRO: CustomTkinter ausente & exit /b 1)
pip show opencv-python >nul 2>&1 || (echo [X] ERRO: OpenCV ausente & exit /b 1)
echo [OK] Ambiente validado
exit /b 0