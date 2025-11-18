param(
    [string]$AppPath = "$env:ProgramFiles\EditorFotos3x4"
)

# Verificar privilégios
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Execute como Administrador" -ForegroundColor Red
    Write-Host "Clique com botao direito > Executar como administrador" -ForegroundColor Yellow
    Read-Host "`nPressione Enter para sair"
    exit 1
}

$parent = Split-Path $AppPath
$backups = Get-ChildItem -Path $parent -Directory -Filter "*backup*" |
           Sort-Object LastWriteTime -Descending

if ($backups.Count -eq 0) {
    Write-Host "Nenhum backup encontrado em: $parent" -ForegroundColor Red
    Read-Host "`nPressione Enter para sair"
    exit 1
}

Write-Host "=== ROLLBACK HELPER - Editor Fotos 3x4 ===" -ForegroundColor Cyan
Write-Host "`nBackups disponiveis:" -ForegroundColor White
for ($i = 0; $i -lt $backups.Count; $i++) {
    $size = (Get-ChildItem $backups[$i].FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  [$i] $($backups[$i].Name) - $($backups[$i].LastWriteTime) - $([math]::Round($size, 2))MB" -ForegroundColor Yellow
}

$choice = Read-Host "`nEscolha o numero do backup para restaurar"

if ([int]::TryParse($choice, [ref]$null) -and [int]$choice -ge 0 -and [int]$choice -lt $backups.Count) {
    $backup = $backups[[int]$choice]
    
    Write-Host "`nRestaurando de: $($backup.Name)..." -ForegroundColor Cyan
    
    # Verificar se aplicação está em execução
    $process = Get-Process "Editor_fotos_3x4" -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Fechando aplicacao..." -ForegroundColor Yellow
        $process | Stop-Process -Force
        Start-Sleep -Seconds 2
    }
    
    try {
        # Backup da versão atual antes de restaurar
        $currentBackup = "$AppPath.antes_rollback_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        if (Test-Path $AppPath) {
            Write-Host "Fazendo backup da versao atual..." -ForegroundColor Yellow
            Copy-Item -Path $AppPath -Destination $currentBackup -Recurse -Force
        }
        
        # Remover versão atual
        if (Test-Path $AppPath) {
            Remove-Item -Path $AppPath -Recurse -Force -ErrorAction Stop
        }
        
        # Restaurar backup
        Copy-Item -Path $backup.FullName -Destination $AppPath -Recurse -Force -ErrorAction Stop
        
        Write-Host "`n=== ROLLBACK CONCLUIDO ===" -ForegroundColor Green
        Write-Host "Aplicacao restaurada com sucesso!" -ForegroundColor Green
        Write-Host "Versao atual foi salva em: $currentBackup" -ForegroundColor Cyan
        
        # Oferecer para iniciar aplicação
        $start = Read-Host "`nDeseja iniciar o Editor de Fotos 3x4? (S/N)"
        if ($start -eq 'S' -or $start -eq 's') {
            Start-Process "$AppPath\Editor_fotos_3x4.exe"
        }
    }
    catch {
        Write-Host "`nERRO durante rollback: $($_.Exception.Message)" -ForegroundColor Red
        
        # Tentar restaurar backup de emergência
        if (Test-Path $currentBackup) {
            Write-Host "Tentando reverter para versao anterior..." -ForegroundColor Yellow
            try {
                if (Test-Path $AppPath) {
                    Remove-Item -Path $AppPath -Recurse -Force
                }
                Copy-Item -Path $currentBackup -Destination $AppPath -Recurse -Force
                Write-Host "Versao anterior restaurada." -ForegroundColor Green
            }
            catch {
                Write-Host "ERRO CRITICO: Nao foi possivel reverter. Reinstale a aplicacao." -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "`nOpcao invalida" -ForegroundColor Red
}

Read-Host "`nPressione Enter para sair"