# Script para criar patch comparando versões
# Salvar como: build/create-patch.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$BaseVersion,
    
    [Parameter(Mandatory=$true)]
    [string]$NewVersion,
    
    [Parameter(Mandatory=$true)]
    [string]$BasePath,
    
    [Parameter(Mandatory=$true)]
    [string]$NewPath,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

function Get-FileHashMD5 {
    param([string]$FilePath)
    try {
        $hash = Get-FileHash -Path $FilePath -Algorithm MD5
        return $hash.Hash
    } catch {
        return $null
    }
}

function Compare-Files {
    param([string]$File1, [string]$File2)
    if (-not (Test-Path $File1) -or -not (Test-Path $File2)) {
        return $false
    }
    $hash1 = Get-FileHashMD5 $File1
    $hash2 = Get-FileHashMD5 $File2
    return ($hash1 -eq $hash2)
}

Write-Host "Criando patch..." -ForegroundColor Cyan
Write-Host "  Base: $BaseVersion"
Write-Host "  Nova: $NewVersion"
Write-Host "  Path Base: $BasePath"
Write-Host "  Path Novo: $NewPath"

# Validar caminhos
if (-not (Test-Path $BasePath)) {
    Write-Host "ERRO: Path base nao encontrado: $BasePath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $NewPath)) {
    Write-Host "ERRO: Path novo nao encontrado: $NewPath" -ForegroundColor Red
    exit 1
}

# Criar pasta output
if (Test-Path $OutputPath) {
    Remove-Item $OutputPath -Recurse -Force
}
New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null

# Normalizar caminhos
$BasePath = (Resolve-Path $BasePath).Path.TrimEnd('\', '/')
$NewPath = (Resolve-Path $NewPath).Path.TrimEnd('\', '/')

Write-Host "`nBuscando arquivos em: $NewPath" -ForegroundColor Cyan

# Obter arquivos (excluir temporários)
$newFiles = Get-ChildItem -Path $NewPath -Recurse -File | Where-Object {
    $_.Name -notmatch '\.(pdb|tmp|log|cache)$' -and
    $_.Directory.Name -notmatch '__pycache__|\.pytest_cache|node_modules'
}

Write-Host "Total de arquivos: $($newFiles.Count)" -ForegroundColor Cyan

$modifiedFiles = @()
$newFilesAdded = @()
$totalProcessed = 0

Write-Host "`nComparando arquivos..." -ForegroundColor Cyan

foreach ($newFile in $newFiles) {
    $totalProcessed++
    
    # Calcular caminho relativo
    $fullPath = $newFile.FullName
    if ($fullPath.StartsWith($NewPath)) {
        $relativePath = $fullPath.Substring($NewPath.Length + 1)
    } else {
        Write-Host "  [SKIP] Caminho invalido: $fullPath" -ForegroundColor Red
        continue
    }
    
    $baseFile = Join-Path $BasePath $relativePath
    
    # Arquivo novo?
    if (-not (Test-Path $baseFile)) {
        Write-Host "  [NOVO] $relativePath" -ForegroundColor Green
        $newFilesAdded += $relativePath
        
        $destPath = Join-Path $OutputPath $relativePath
        $destDir = Split-Path $destPath -Parent
        
        if (-not (Test-Path $destDir)) {
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }
        
        Copy-Item $newFile.FullName $destPath -Force
    }
    # Arquivo modificado?
    elseif (-not (Compare-Files $baseFile $newFile.FullName)) {
        Write-Host "  [MOD]  $relativePath" -ForegroundColor Yellow
        $modifiedFiles += $relativePath
        
        $destPath = Join-Path $OutputPath $relativePath
        $destDir = Split-Path $destPath -Parent
        
        if (-not (Test-Path $destDir)) {
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }
        
        Copy-Item $newFile.FullName $destPath -Force
    }
}

$totalChanges = $modifiedFiles.Count + $newFilesAdded.Count

Write-Host "`nResumo:" -ForegroundColor Cyan
Write-Host "  Arquivos processados: $totalProcessed"
Write-Host "  Arquivos modificados: $($modifiedFiles.Count)" -ForegroundColor Yellow
Write-Host "  Arquivos novos: $($newFilesAdded.Count)" -ForegroundColor Green
Write-Host "  Total de mudancas: $totalChanges"

if ($totalChanges -eq 0) {
    Write-Host "`nNenhuma alteracao detectada!" -ForegroundColor Yellow
    Remove-Item $OutputPath -Recurse -Force -ErrorAction SilentlyContinue
    exit 0
}

# Criar manifest.json
$manifest = @{
    baseVersion = $BaseVersion
    newVersion = $NewVersion
    createdAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    modifiedFiles = $modifiedFiles
    newFiles = $newFilesAdded
    totalChanges = $totalChanges
    patchSize = 0
}

# Calcular tamanho
$patchFiles = Get-ChildItem -Path $OutputPath -Recurse -File
$totalSize = ($patchFiles | Measure-Object -Property Length -Sum).Sum
$manifest.patchSize = $totalSize

# Salvar manifest
$manifestPath = Join-Path $OutputPath "manifest.json"
$manifest | ConvertTo-Json -Depth 10 | Set-Content $manifestPath -Encoding UTF8

Write-Host "`nManifest criado: manifest.json" -ForegroundColor Green
Write-Host "  Tamanho: $([Math]::Round($totalSize / 1MB, 2)) MB"
Write-Host "`nPatch criado em: $OutputPath" -ForegroundColor Green
