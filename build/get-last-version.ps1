# Script para detectar última versão disponível nas releases
# Editor Fotos 3x4 - Build System

$ErrorActionPreference = "SilentlyContinue"

$releasesPath = Join-Path $PSScriptRoot "..\releases"

# Verificar se pasta releases existe
if (-not (Test-Path $releasesPath)) {
    exit
}

# Buscar pastas com padrão de versão (X.Y.Z)
$versions = Get-ChildItem -Path $releasesPath -Directory | 
    Where-Object { $_.Name -match '^\d+\.\d+\.\d+$' } |
    ForEach-Object {
        $parts = $_.Name.Split('.')
        [PSCustomObject]@{
            Name = $_.Name
            Major = [int]$parts[0]
            Minor = [int]$parts[1]
            Patch = [int]$parts[2]
            FullPath = $_.FullName
        }
    } |
    Sort-Object Major, Minor, Patch -Descending

# Retornar última versão
if ($versions) {
    # Validar que tem o executável principal
    $lastVersion = $versions[0]
    $exePath = Join-Path $lastVersion.FullPath "Editor_fotos_3x4.exe"
    
    if (Test-Path $exePath) {
        Write-Output $lastVersion.Name
    }
}
