# Script para obter versÃ£o do projeto
$versionFile = Join-Path $PSScriptRoot "..\version.txt"
$fallbackVersion = "3.0.2"

# Tentar ler de version.txt
if (Test-Path $versionFile) {
    $version = Get-Content $versionFile -ErrorAction SilentlyContinue
    if ($version) {
        # Remover 'v' se existir e espaÃ§os em branco
        $version = $version.Trim() -replace '^v', ''
        if ($version -match '^\d+\.\d+\.\d+$') {
            Write-Output $version
            exit 0
        }
    }
}

# Tentar ler de main.py como fallback
$mainPy = Join-Path $PSScriptRoot "..\main.py"
if (Test-Path $mainPy) {
    $content = Get-Content $mainPy -Raw
    if ($content -match 'Vers[aÃ£]o\s+(\d+\.\d+\.\d+)') {
        Write-Output $matches[1]
        exit 0
    }
}

# Tentar ler de Editor_Fotos_3x4.spec
$specFile = Join-Path $PSScriptRoot "..\Editor_Fotos_3x4.spec"
if (Test-Path $specFile) {
    $content = Get-Content $specFile -Raw
    if ($content -match "version\s*=\s*'(\d+\.\d+\.\d+)'") {
        Write-Output $matches[1]
        exit 0
    }
}

# Retornar versÃ£o padrÃ£o
Write-Output $fallbackVersion