@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo  BUILD PATCH - Editor Fotos 3x4
echo ===============================================

set "ROOT_DIR=%~dp0.."
cd /d "%ROOT_DIR%"

:: Ler versão atual CORRIGIDO
set NEW_VERSION=
for /f "delims=" %%v in ('powershell -NoProfile -Command "if (Test-Path 'version.txt') { (Get-Content 'version.txt' -Raw).Trim() -replace '^v','' -replace '\s','' } else { '3.1.2' }"') do set NEW_VERSION=%%v
if "%NEW_VERSION%"=="" set NEW_VERSION=3.1.2

echo Versao detectada: %NEW_VERSION%

:: Auto-detectar versão base
for /f %%v in ('powershell -NoProfile -Command "$dirs = Get-ChildItem -Path 'releases' -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d+\.\d+\.\d+$' } | Sort-Object Name -Descending; if ($dirs) { $dirs[0].Name }"') do set DETECTED_VERSION=%%v

if not "%DETECTED_VERSION%"=="" (
    echo Versao base detectada: %DETECTED_VERSION%
    set /p BASE_VERSION="Confirme [Enter] ou digite outra: "
    if "!BASE_VERSION!"=="" set BASE_VERSION=%DETECTED_VERSION%
) else (
    set /p BASE_VERSION="Versao base: "
)

echo.
echo Base: %BASE_VERSION% ^| Nova: %NEW_VERSION%
echo.

if "%BASE_VERSION%"=="" (
    echo ERRO: Versao base obrigatoria
    pause
    exit /b 1
)

if not exist "releases\%BASE_VERSION%" (
    echo ERRO: Versao base %BASE_VERSION% nao encontrada
    pause
    exit /b 1
)

:: [1/10] Limpar
echo [1/10] Limpando builds anteriores...
if exist "src\dist" rd /s /q "src\dist" 2>nul
if exist "src\build" rd /s /q "src\build" 2>nul
if exist "src\modules\__pycache__" rd /s /q "src\modules\__pycache__" 2>nul

:: [2/10] C# x64
echo [2/10] Compilando componente C# x64...
cd src\cs_components\FastImageOps
dotnet publish -c Release -r win-x64 --self-contained true /p:PublishSingleFile=false /p:DebugType=None /p:DebugSymbols=false --nologo -v q >nul 2>&1
if errorlevel 1 (
    echo ERRO: Compilacao C# x64 falhou
    cd ..\..\..
    pause
    exit /b 1
)
cd ..\..\..

:: [3/10] C# x86
echo [3/10] Compilando componente C# x86...
cd src\cs_components\FastImageOps
dotnet publish -c Release -r win-x86 --self-contained true /p:PublishSingleFile=false /p:DebugType=None /p:DebugSymbols=false --nologo -v q >nul 2>&1
if errorlevel 1 (
    echo ERRO: Compilacao C# x86 falhou
    cd ..\..\..
    pause
    exit /b 1
)
cd ..\..\..

:: [4/10] Organizar DLLs
echo [4/10] Organizando componentes C#...
set "CS_OUTPUT_X64=src\cs_components\FastImageOps\bin\Release\net8.0\win-x64\publish"
set "CS_OUTPUT_X86=src\cs_components\FastImageOps\bin\Release\net8.0\win-x86\publish"
set "CS_TARGET=src\modules\cs_dlls"

if not exist "%CS_TARGET%\x64" mkdir "%CS_TARGET%\x64"
if not exist "%CS_TARGET%\x86" mkdir "%CS_TARGET%\x86"

xcopy "%CS_OUTPUT_X64%\*.dll" "%CS_TARGET%\x64\" /Y /Q >nul
xcopy "%CS_OUTPUT_X64%\*.exe" "%CS_TARGET%\x64\" /Y /Q >nul
xcopy "%CS_OUTPUT_X64%\*.json" "%CS_TARGET%\x64\" /Y /Q >nul
xcopy "%CS_OUTPUT_X86%\*.dll" "%CS_TARGET%\x86\" /Y /Q >nul
xcopy "%CS_OUTPUT_X86%\*.exe" "%CS_TARGET%\x86\" /Y /Q >nul
xcopy "%CS_OUTPUT_X86%\*.json" "%CS_TARGET%\x86\" /Y /Q >nul

:: [5/10] Assinar C#
echo [5/10] Assinando componentes C#...
if exist "build\sign.ps1" (
    for %%f in ("%CS_TARGET%\x64\*.exe" "%CS_TARGET%\x86\*.exe") do (
        if exist "%%f" (
            powershell -ExecutionPolicy Bypass -File "build\sign.ps1" -ExePath "%%f" >nul 2>&1
        )
    )
)

:: [6/10] Dependências
echo [6/10] Atualizando dependencias Python...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

:: [7/10] PyInstaller
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

:: [8/10] Assinar EXE
echo [8/10] Assinando executavel principal...
set "MAIN_EXE=src\dist\editor_fotos\Editor_fotos_3x4.exe"
if exist "%MAIN_EXE%" (
    if exist "build\sign.ps1" (
        powershell -ExecutionPolicy Bypass -File "build\sign.ps1" -ExePath "%MAIN_EXE%" >nul 2>&1
    )
)

:: [9/10] Criar patch - CORRIGIDO
echo [9/10] Criando patch por comparacao...
set "PATCH_DIR=releases\patch_%NEW_VERSION%"

if not exist "build\create-patch.ps1" (
    echo ERRO: Script create-patch.ps1 nao encontrado em build\
    echo Verifique se o arquivo existe em: %CD%\build\create-patch.ps1
    pause
    exit /b 1
)

powershell -ExecutionPolicy Bypass -File "build\create-patch.ps1" -BaseVersion "%BASE_VERSION%" -NewVersion "%NEW_VERSION%" -BasePath "releases\%BASE_VERSION%" -NewPath "src\dist\editor_fotos" -OutputPath "%PATCH_DIR%"

if errorlevel 1 (
    echo ERRO: Falha ao criar patch
    pause
    exit /b 1
)

if not exist "%PATCH_DIR%\manifest.json" (
    echo.
    echo ===============================================
    echo  AVISO: NENHUMA ALTERACAO DETECTADA
    echo ===============================================
    echo Versoes %BASE_VERSION% e %NEW_VERSION% sao identicas
    pause
    exit /b 0
)

:: [10/10] Instalador patch
echo [10/10] Gerando instalador de patch...

if exist "build\version.ps1" (
    powershell -ExecutionPolicy Bypass -File "build\version.ps1" -NewVersion "%NEW_VERSION%" >nul 2>&1
)

set "OUTPUT_DIR=releases\Output"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "%INNO_PATH%" (
    "%INNO_PATH%" "build\installer-patch.iss" /Q
    
    if errorlevel 1 (
        echo ERRO: Falha ao compilar instalador
        pause
        exit /b 1
    )
    
    echo.
    echo ===============================================
    echo  PATCH CONCLUIDO COM SUCESSO
    echo ===============================================
    echo Base: %BASE_VERSION% -^> Nova: %NEW_VERSION%
    echo.
    
    set "PATCH_FILE=%OUTPUT_DIR%\EditorFotos3x4_Patch_%NEW_VERSION%.exe"
    if exist "!PATCH_FILE!" (
        for %%f in ("!PATCH_FILE!") do (
            set /a SIZE_MB=%%~zf/1048576
            echo Instalador: !PATCH_FILE!
            echo Tamanho: !SIZE_MB! MB
        )
    )
    
    echo.
    echo Arquivos alterados:
    powershell -NoProfile -Command "$m = Get-Content '%PATCH_DIR%\manifest.json' | ConvertFrom-Json; $m.modifiedFiles | ForEach-Object { Write-Host '  *' $_ }"
    echo ===============================================
) else (
    echo.
    echo ===============================================
    echo  PATCH CRIADO (SEM INSTALADOR)
    echo ===============================================
    echo AVISO: Inno Setup nao encontrado
    echo Patch: %PATCH_DIR%
    echo ===============================================
)

:: Limpar
echo.
echo Limpando arquivos temporarios...
if exist "src\dist" rd /s /q "src\dist" 2>nul
if exist "src\build" rd /s /q "src\build" 2>nul
if exist "src\modules\__pycache__" rd /s /q "src\modules\__pycache__" 2>nul
if exist "src\cs_components\FastImageOps\bin" rd /s /q "src\cs_components\FastImageOps\bin" 2>nul
if exist "src\cs_components\FastImageOps\obj" rd /s /q "src\cs_components\FastImageOps\obj" 2>nul
if exist "src\modules\cs_dlls" rd /s /q "src\modules\cs_dlls" 2>nul

echo Concluido!
pause
