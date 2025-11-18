param(
    [Parameter(Mandatory=$true)]
    [string]$ExePath
)

if (-not (Test-Path $ExePath)) {
    Write-Error "Arquivo nao encontrado: $ExePath"
    exit 1
}

# Tentar usar certificado existente ou criar temporario
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | 
    Where-Object {$_.Subject -like "*EditorFotos*" -or $_.Subject -like "*Samuel Fernandes*"} | 
    Select-Object -First 1

if (-not $cert) {
    # Criar certificado self-signed temporario
    Write-Host "Criando certificado temporario..." -ForegroundColor Yellow
    $cert = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject "CN=Editor Fotos 3x4 Dev Certificate" `
        -KeySpec Signature `
        -KeyUsage DigitalSignature `
        -FriendlyName "EditorFotos3x4 Dev" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter (Get-Date).AddYears(2)
}

# Assinar arquivo
try {
    # Tentar com timestamp server primario
    Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com" | Out-Null
    Write-Host "Assinado com sucesso: $ExePath" -ForegroundColor Green
    exit 0
} catch {
    try {
        # Fallback para servidor alternativo
        Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -TimestampServer "http://timestamp.comodoca.com/authenticode" | Out-Null
        Write-Host "Assinado com sucesso (servidor alternativo): $ExePath" -ForegroundColor Green
        exit 0
    } catch {
        # Assinar sem timestamp
        Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert | Out-Null
        Write-Warning "Assinado sem timestamp: $ExePath"
        exit 0
    }
}