@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo  BUILD COMPLETO - Editor Fotos 3x4
echo ===============================================

set "ROOT_DIR=%~dp0.."
cd /d "%ROOT_DIR%"

:: Detectar versão
for /f "tokens=*" %%v in ('powershell -NoProfile -Command "(Get-Content 'version.txt' -ErrorAction SilentlyContinue) -replace 'v','' 2>nul"') do set VERSION=%%v
if "%VERSION%"=="" set VERSION=3.1.0

echo Versao: %VERSION%
echo Root: %ROOT_DIR%
echo.

:: [0/10] Validar ambiente
call "build\validate-env.bat"
if errorlevel 1 (
    echo Corrija as dependencias antes de continuar
    pause
    exit /b 1
)

:: Verificar .NET SDK
echo [0/10] Verificando dependencias...
dotnet --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: .NET 8 SDK nao encontrado
    pause
    exit /b 1
)

py --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: py nao encontrado
    pause
    exit /b 1
)

:: [1/10] Limpar builds anteriores
echo [1/10] Limpando builds anteriores...
if exist "src\dist" rd /s /q "src\dist" 2>nul
if exist "src\build" rd /s /q "src\build" 2>nul
if exist "src\cs_components\FastImageOps\bin" rd /s /q "src\cs_components\FastImageOps\bin" 2>nul
if exist "src\cs_components\FastImageOps\obj" rd /s /q "src\cs_components\FastImageOps\obj" 2>nul

:: [2/10] Restaurar dependências C#
echo [2/10] Restaurando dependencias C#...
cd src\cs_components\FastImageOps
dotnet restore --nologo -v q
if errorlevel 1 (
    echo ERRO: Falha ao restaurar dependencias C#
    cd ..\..\..
    pause
    exit /b 1
)

:: [3/10] Compilar C# x64 + x86
echo [3/10] Compilando C# x64...
dotnet publish -c Release -r win-x64 --self-contained true ^
    /p:PublishSingleFile=false /p:PublishTrimmed=false --nologo -v q
echo [3/10] Compilando C# x86...
dotnet publish -c Release -r win-x86 --self-contained true ^
    /p:PublishSingleFile=false /p:PublishTrimmed=false --nologo -v q

if errorlevel 1 (
    echo ERRO: Compilacao C# falhou
    cd ..\..\..
    pause
    exit /b 1
)
cd ..\..\..

:: [4/10] Copiar DLLs C# - OTIMIZADO
echo [4/10] Copiando componentes C# otimizados...
set "CS_OUTPUT_X64=src\cs_components\FastImageOps\bin\Release\net8.0\win-x64\publish"
set "CS_OUTPUT_X86=src\cs_components\FastImageOps\bin\Release\net8.0\win-x86\publish"
set "CS_TARGET=src\modules\cs_dlls"

:: Criar pastas x64 e x86
if not exist "%CS_TARGET%\x64" mkdir "%CS_TARGET%\x64"
if not exist "%CS_TARGET%\x86" mkdir "%CS_TARGET%\x86"

:: Copiar AMBAS arquiteturas
xcopy "%CS_OUTPUT_X64%\*.dll" "%CS_TARGET%\x64\" /Y /Q >nul
xcopy "%CS_OUTPUT_X64%\*.exe" "%CS_TARGET%\x64\" /Y /Q >nul
xcopy "%CS_OUTPUT_X64%\*.json" "%CS_TARGET%\x64\" /Y /Q >nul
xcopy "%CS_OUTPUT_X86%\*.dll" "%CS_TARGET%\x86\" /Y /Q >nul
xcopy "%CS_OUTPUT_X86%\*.exe" "%CS_TARGET%\x86\" /Y /Q >nul
xcopy "%CS_OUTPUT_X86%\*.json" "%CS_TARGET%\x86\" /Y /Q >nul
echo DLLs x64 e x86 copiadas

:: [5/10] Assinar executável C#
echo [5/10] Assinando componente C#...
set "CS_EXE=%CS_TARGET%\FastImageOps.exe"
if exist "%CS_EXE%" (
    powershell -ExecutionPolicy Bypass -File "build\sign.ps1" -ExePath "%CS_EXE%" >nul 2>&1
    if errorlevel 1 echo AVISO: Assinatura opcional nao aplicada
)

:: [6/10] Instalar dependências py
echo [6/10] Instalando dependencias py...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias py
    pause
    exit /b 1
)

:: [7/10] Criar executável Python
echo [7/10] Criando executavel com PyInstaller...
cd src
pyinstaller Editor_Fotos_3x4.spec --clean --noconfirm >nul 2>&1
if errorlevel 1 (
    echo ERRO: Falha no PyInstaller
    cd ..
    pause
    exit /b 1
)
cd ..

:: [8/10] Assinar executável principal
echo [8/10] Assinando executavel principal...
set "MAIN_EXE=src\dist\editor_fotos\Editor_fotos_3x4.exe"
if exist "%MAIN_EXE%" (
    powershell -ExecutionPolicy Bypass -File "build\sign.ps1" -ExePath "%MAIN_EXE%" >nul 2>&1
    if errorlevel 1 echo AVISO: Assinatura opcional nao aplicada
)

:: [9/10] Copiar para releases
echo [9/10] Organizando release %VERSION%...
set "RELEASE_DIR=releases\%VERSION%"

if exist "%RELEASE_DIR%" (
    echo Fazendo backup da versao anterior...
    if exist "%RELEASE_DIR%.old" rd /s /q "%RELEASE_DIR%.old" 2>nul
    move "%RELEASE_DIR%" "%RELEASE_DIR%.old" >nul 2>&1
)

mkdir "%RELEASE_DIR%" 2>nul
xcopy "src\dist\editor_fotos\*" "%RELEASE_DIR%\" /E /Y /Q >nul
if errorlevel 1 (
    echo ERRO: Falha ao copiar arquivos
    pause
    exit /b 1
)

copy "README.md" "%RELEASE_DIR%\" >nul 2>&1
copy "LICENSE.txt" "%RELEASE_DIR%\" >nul 2>&1
copy "haarcascade_frontalface_default.xml" "%RELEASE_DIR%\" >nul 2>&1

del "%RELEASE_DIR%\*.pyc" /S /Q 2>nul
del "%RELEASE_DIR%\*.pyo" /S /Q 2>nul
del "%RELEASE_DIR%\*.pdb" /S /Q 2>nul

:: [10/10] Criar instalador
echo [10/10] Criar instalador...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "%INNO_PATH%" (
    echo.
    echo [10/10] Compilando instalador...
    powershell -ExecutionPolicy Bypass -File "build\version.ps1"
    "%INNO_PATH%" "build\installer-full.iss" "/Q"
    if not errorlevel 1 echo Instalador criado com sucesso!
)

if exist "%RELEASE_DIR%.old" rd /s /q "%RELEASE_DIR%.old" 2>nul

for %%f in ("%RELEASE_DIR%\Editor_fotos_3x4.exe") do set EXE_SIZE=%%~zf
set /a EXE_SIZE_MB=%EXE_SIZE%/1048576

echo.
echo ===============================================
echo  BUILD CONCLUIDO COM SUCESSO!
echo ===============================================
echo Versao: %VERSION%
echo Executavel: %RELEASE_DIR%\Editor_fotos_3x4.exe (~%EXE_SIZE_MB%MB)
echo ===============================================

pause

:: Limpeza forçada
echo.
echo Limpando arquivos temporarios...
if exist "src\dist" rd /s /q "src\dist" 2>nul
if exist "src\build" rd /s /q "src\build" 2>nul
if exist "src\modules\__pycache__" rd /s /q "src\modules\__pycache__" 2>nul
if exist "src\cs_components\FastImageOps\bin" rd /s /q "src\cs_components\FastImageOps\bin" 2>nul
if exist "src\cs_components\FastImageOps\obj" rd /s /q "src\cs_components\FastImageOps\obj" 2>nul
if exist "src\modules\cs_dlls" rd /s /q "src\modules\cs_dlls" 2>nul