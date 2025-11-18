# Script para atualizar versão em todos os arquivos
param([string]$NewVersion = "")

$ErrorActionPreference = "Stop"
$versionFile = Join-Path $PSScriptRoot "..\version.txt"

function Test-VersionFormat {
    param([string]$Version)
    return $Version -match '^\d+\.\d+\.\d+$'
}

# Obter versão atual
if (Test-Path $versionFile) {
    $currentVersion = (Get-Content $versionFile -Raw).Trim() -replace '^v', '' -replace '\s', ''
} else {
    $currentVersion = "3.1.0"
    New-Item -Path $versionFile -ItemType File -Force | Out-Null
    Set-Content $versionFile "v$currentVersion" -NoNewline
    Write-Host "Arquivo version.txt criado: $currentVersion" -ForegroundColor Yellow
}

if ($NewVersion) {
    if (-not (Test-VersionFormat $NewVersion)) {
        Write-Host "ERRO: Formato invalido. Use: X.Y.Z" -ForegroundColor Red
        exit 1
    }
    $version = $NewVersion
    Set-Content $versionFile "v$version" -NoNewline
    Write-Host "Versao atualizada: $version" -ForegroundColor Cyan
} else {
    $version = $currentVersion
    Write-Host "Usando versao atual: $version" -ForegroundColor Green
}

# ARQUIVOS CORRIGIDOS
$files = @(
    @{
        Path = Join-Path $PSScriptRoot "installer-full.iss"
        Pattern = '#define MyAppVersion "[\d\.]+"'
        Replace = "#define MyAppVersion `"$version`""
        Description = "Instalador Full"
    },
    @{
        Path = Join-Path $PSScriptRoot "installer-patch.iss"
        Pattern = '#define MyAppVersion "[\d\.]+"'
        Replace = "#define MyAppVersion `"$version`""
        Description = "Instalador Patch"
    },
    @{
        Path = Join-Path $PSScriptRoot "..\src\main.py"
        Pattern = 'VERSION = Path\("\.\.\/version\.txt"\)\.read_text\(\)\.strip\(\) if Path\("\.\.\/version\.txt"\)\.exists\(\) else "[\d\.]+"'
        Replace = "VERSION = Path(`"../version.txt`").read_text().strip() if Path(`"../version.txt`").exists() else `"$version`""
        Description = "main.py"
    }
)

$updated = 0
$failed = 0

Write-Host "`nAtualizando arquivos..." -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

foreach ($file in $files) {
    $filePath = $file.Path
    
    if (-not (Test-Path $filePath)) {
        Write-Host "  [SKIP] $($file.Description): Nao encontrado" -ForegroundColor Yellow
        continue
    }
    
    try {
        $content = Get-Content $filePath -Raw -Encoding UTF8
        $newContent = $content -replace $file.Pattern, $file.Replace
        
        if ($content -eq $newContent) {
            Write-Host "  [OK]   $($file.Description): Sem alteracoes" -ForegroundColor Gray
        } else {
            Set-Content $filePath $newContent -NoNewline -Encoding UTF8
            Write-Host "  [UPD]  $($file.Description): Atualizado" -ForegroundColor Green
            $updated++
        }
    } catch {
        Write-Host "  [ERRO] $($file.Description): $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ("=" * 60) -ForegroundColor Gray

if ($failed -gt 0) {
    Write-Host "`nConcluido com erros:" -ForegroundColor Red
    Write-Host "  Atualizados: $updated" -ForegroundColor Green
    Write-Host "  Falharam: $failed" -ForegroundColor Red
    exit 1
} elseif ($updated -gt 0) {
    Write-Host "`nVersao atualizada: $version" -ForegroundColor Green
    Write-Host "  Arquivos atualizados: $updated" -ForegroundColor Cyan
} else {
    Write-Host "`nTodos os arquivos atualizados: $version" -ForegroundColor Green
}

Write-Host "`nValidando..." -ForegroundColor Cyan

$validation = @{
    Full = (Get-Content (Join-Path $PSScriptRoot "installer-full.iss") -Raw) -match "#define MyAppVersion `"$version`""
    Patch = (Get-Content (Join-Path $PSScriptRoot "installer-patch.iss") -Raw) -match "#define MyAppVersion `"$version`""
}

$allValid = $true
foreach ($key in $validation.Keys) {
    if ($validation[$key]) {
        Write-Host "  [OK] $key : $version" -ForegroundColor Green
    } else {
        Write-Host "  [ERRO] $key : Incorreto" -ForegroundColor Red
        $allValid = $false
    }
}

if ($allValid) {
    Write-Host "`nValidacao concluida!" -ForegroundColor Green
} else {
    Write-Host "`nValidacao falhou!" -ForegroundColor Red
    exit 1
}

# Validação cruzada
Write-Host "`nValidando consistência..." -ForegroundColor Cyan
$errors = @()

foreach ($file in $files) {
    if (Test-Path $file.Path) {
        $content = Get-Content $file.Path -Raw -Encoding UTF8
        if ($content -notmatch [regex]::Escape($version)) {
            $errors += "  [ERRO] $($file.Description): Versão inconsistente"
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "`nErros de validação:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host $_ }
    exit 1
}

Write-Host "Validação concluída com sucesso!" -ForegroundColor Green