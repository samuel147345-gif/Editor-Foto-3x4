#define MyAppName "Editor de Fotos 3x4"
#define MyAppVersion "3.1.0"
#define MyAppPublisher "Samuel Fernandes - DP"
#define MyAppExeName "Editor_fotos_3x4.exe"
#define MyAppId "7A8B9C2D-4E5F-6A7B-8C9D-0E1F2A3B4C5D"

[Setup]
AppId={{{#MyAppId}}
AppName={#MyAppName} (Patch)
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={code:GetInstallDir}
OutputDir={#SourcePath}..\releases\Output
OutputBaseFilename=EditorFotos3x4_Patch_{#MyAppVersion}
SetupIconFile={#SourcePath}..\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible x86compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableWelcomePage=yes
DisableDirPage=yes
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription=Patch para {#MyAppName}
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName} Patch
VersionInfoProductVersion={#MyAppVersion}
MinVersion=10.0

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourcePath}..\releases\patch_{#MyAppVersion}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\EditorFotos3x4"
Type: filesandordirs; Name: "{userappdata}\.editor_fotos_3x4"
Type: dirifempty; Name: "{app}"

[Code]
var
  BackupPath: String;
  InstallPath: String;
  InstalledVersion: String;
  InstalledArchitecture: String;
  IsX64System: Boolean;

function GetArchitectureName: String;
begin
  if IsX64System then
    Result := 'x64'
  else
    Result := 'x86';
end;

function GetInstallationInfo(var Version, Path, Arch: String): Boolean;
var
  UninstallKey: String;
begin
  Result := False;
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1';
  
  if RegQueryStringValue(HKCU, UninstallKey, 'DisplayVersion', Version) and
     RegQueryStringValue(HKCU, UninstallKey, 'InstallLocation', Path) then
  begin
    RegQueryStringValue(HKCU, 'Software\EditorFotos3x4', 'Architecture', Arch);
    if Arch = '' then Arch := 'x64';
    Result := True;
    Exit;
  end;
  
  if RegQueryStringValue(HKLM, UninstallKey, 'DisplayVersion', Version) and
     RegQueryStringValue(HKLM, UninstallKey, 'InstallLocation', Path) then
  begin
    RegQueryStringValue(HKLM, 'Software\EditorFotos3x4', 'Architecture', Arch);
    if Arch = '' then Arch := 'x64';
    Result := True;
    Exit;
  end;
  
  Path := ExpandConstant('{autopf}\EditorFotos3x4');
  if FileExists(Path + '\{#MyAppExeName}') then
  begin
    Version := 'unknown';
    Arch := GetArchitectureName;
    Result := True;
  end;
end;

function GetInstallDir(Param: String): String;
begin
  if InstallPath <> '' then
    Result := InstallPath
  else
    Result := ExpandConstant('{autopf}\EditorFotos3x4');
end;

function InitializeSetup: Boolean;
begin
  Result := False;
  IsX64System := IsWin64;
  
  Log('Sistema: ' + GetArchitectureName);
  
  if not GetInstallationInfo(InstalledVersion, InstallPath, InstalledArchitecture) then
  begin
    MsgBox('Editor de Fotos 3x4 nao encontrado.' + #13#10 + 
           'Instale a versao completa primeiro.', mbError, MB_OK);
    Exit;
  end;
  
  Log('Instalacao: ' + InstallPath);
  Log('Versao: ' + InstalledVersion);
  Log('Arquitetura: ' + InstalledArchitecture);
  
  if (InstalledArchitecture <> GetArchitectureName) and (InstalledArchitecture <> '') then
  begin
    if MsgBox('AVISO: Arquitetura diferente.' + #13#10 +
           'Instalado: ' + InstalledArchitecture + #13#10 +
           'Sistema: ' + GetArchitectureName + #13#10 + #13#10 +
           'Continuar?', mbConfirmation, MB_YESNO) = IDNO then
      Exit;
  end;
  
  Result := True;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  BackupCmd: String;
  TempBat: String;
begin
  Result := '';
  NeedsRestart := False;
  
  if InstallPath = '' then
    InstallPath := ExpandConstant('{app}');
  
  BackupPath := InstallPath + '.backup_' + GetDateTimeString('yyyymmdd_hhnnss', '-', ':');
  
  Log('Backup: ' + BackupPath);
  
  if DirExists(InstallPath) then
  begin
    TempBat := ExpandConstant('{tmp}\backup.bat');
    BackupCmd := '@echo off' + #13#10 +
                 'chcp 65001 >nul 2>&1' + #13#10 +
                 'echo Criando backup...' + #13#10 +
                 'xcopy "' + InstallPath + '" "' + BackupPath + '\" /E /I /Y /Q >nul 2>&1' + #13#10 +
                 'exit /b %errorlevel%';
    
    SaveStringToFile(TempBat, BackupCmd, False);
    
    if not Exec(ExpandConstant('{cmd}'), '/c "' + TempBat + '"', '', 
                SW_HIDE, ewWaitUntilTerminated, ResultCode) or (ResultCode <> 0) then
    begin
      Result := 'Falha ao criar backup. Codigo: ' + IntToStr(ResultCode);
      Log('ERRO: ' + Result);
      Exit;
    end;
    
    Log('Backup criado');
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  ExePath: String;
  RollbackCmd: String;
  TempBat: String;
begin
  if CurStep = ssPostInstall then
  begin
    ExePath := ExpandConstant('{app}\{#MyAppExeName}');
    
    if not FileExists(ExePath) then
    begin
      Log('ERRO: Executavel nao encontrado');
      
      MsgBox('ERRO: Patch falhou.' + #13#10 +
             'Revertendo...', mbError, MB_OK);
      
      if DirExists(BackupPath) then
      begin
        TempBat := ExpandConstant('{tmp}\rollback.bat');
        RollbackCmd := '@echo off' + #13#10 +
                       'chcp 65001 >nul 2>&1' + #13#10 +
                       'echo Revertendo...' + #13#10 +
                       'rd /s /q "' + InstallPath + '" 2>nul' + #13#10 +
                       'xcopy "' + BackupPath + '\*" "' + InstallPath + '\" /E /I /Y /Q >nul 2>&1' + #13#10 +
                       'exit /b %errorlevel%';
        
        SaveStringToFile(TempBat, RollbackCmd, False);
        
        Exec(ExpandConstant('{cmd}'), '/c "' + TempBat + '"', '', 
             SW_HIDE, ewWaitUntilTerminated, ResultCode);
             
        if ResultCode = 0 then
          MsgBox('Rollback concluido.', mbInformation, MB_OK)
        else
          MsgBox('AVISO: Rollback falhou.' + #13#10 +
                 'Verifique manualmente.', mbError, MB_OK);
      end;
    end
    else
    begin
      Log('Patch aplicado');
      
      RegWriteStringValue(HKCU, 'Software\EditorFotos3x4', 'Version', '{#MyAppVersion}');
      RegWriteStringValue(HKCU, 'Software\EditorFotos3x4', 'Architecture', GetArchitectureName);
      
      MsgBox('Patch {#MyAppVersion} aplicado com sucesso!', mbInformation, MB_OK);
    end;
  end;
end;

procedure DeinitializeSetup;
var
  ResultCode: Integer;
  CleanupCmd: String;
  TempBat: String;
begin
  if DirExists(BackupPath) then
  begin
    Log('Limpando backup');
    
    TempBat := ExpandConstant('{tmp}\cleanup.bat');
    CleanupCmd := '@echo off' + #13#10 +
                  'timeout /t 2 /nobreak >nul' + #13#10 +
                  'rd /s /q "' + BackupPath + '" 2>nul';
    
    SaveStringToFile(TempBat, CleanupCmd, False);
    
    Exec(ExpandConstant('{cmd}'), '/c "' + TempBat + '"', '', 
         SW_HIDE, ewNoWait, ResultCode);
  end;
end;