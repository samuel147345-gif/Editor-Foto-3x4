#define MyAppName "Editor de Fotos 3x4"
#define MyAppVersion "3.1.0"
#define MyAppPublisher "Samuel Fernandes - DP"
#define MyAppExeName "Editor_fotos_3x4.exe"
#define MyAppId "7A8B9C2D-4E5F-6A7B-8C9D-0E1F2A3B4C5D"

[Setup]
AppId={{{#MyAppId}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/editor-fotos
AppSupportURL=https://github.com/editor-fotos/support
AppUpdatesURL=https://github.com/editor-fotos/releases
DefaultDirName={autopf}\EditorFotos3x4
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir={#SourcePath}..\releases\Output
OutputBaseFilename=EditorFotos3x4_Setup_{#MyAppVersion}
SetupIconFile={#SourcePath}..\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

; Suporte x64 e x86 automático
ArchitecturesAllowed=x64compatible x86compatible
ArchitecturesInstallIn64BitMode=x64compatible

UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes
DisableWelcomePage=no
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription=Editor profissional de fotos 3x4
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Requisitos mínimos
MinVersion=10.0

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "Criar atalho na barra de inicialização rápida"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associateimages"; Description: "Associar arquivos de imagem (.jpg, .png, .bmp)"; GroupDescription: "Associações de arquivo:"; Flags: unchecked

[Files]
; Executável principal
Source: "{#SourcePath}..\releases\{#MyAppVersion}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Pasta _internal (EXCLUINDO cs_dlls e __pycache__)
Source: "{#SourcePath}..\releases\{#MyAppVersion}\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "\cs_dlls,\modules\cs_dlls,\modules\__pycache__,\__pycache__,*.pyc,*.pyo"

; DLLs C# - APENAS arquitetura correta em modules/cs_dlls
Source: "{#SourcePath}..\releases\{#MyAppVersion}\_internal\modules\cs_dlls\x64\*"; DestDir: "{app}\_internal\modules\cs_dlls"; Flags: ignoreversion; Check: IsX64
Source: "{#SourcePath}..\releases\{#MyAppVersion}\_internal\modules\cs_dlls\x86\*"; DestDir: "{app}\_internal\modules\cs_dlls"; Flags: ignoreversion; Check: not IsX64

; Recursos essenciais
Source: "{#SourcePath}..\releases\{#MyAppVersion}\_internal\modules\haarcascade_frontalface_default.xml"; DestDir: "{app}"; Flags: ignoreversion

; Ferramentas (rollback)
Source: "{#SourcePath}..\tools\rollback-helper.bat"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{#SourcePath}..\tools\rollback-helper.bat'))
Source: "{#SourcePath}..\tools\rollback-helper.ps1"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{#SourcePath}..\tools\rollback-helper.ps1'))

; Documentação
Source: "{#SourcePath}..\README.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Check: FileExists(ExpandConstant('{#SourcePath}..\README.md'))
Source: "{#SourcePath}..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{#SourcePath}..\LICENSE.txt'))

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Documentação"; Filename: "{app}\README.txt"; Check: FileExists(ExpandConstant('{app}\README.txt'))
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Associações de arquivo
Root: HKCU; Subkey: "Software\Classes\.jpg\OpenWithProgids"; ValueType: string; ValueName: "EditorFotos3x4.Image"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associateimages
Root: HKCU; Subkey: "Software\Classes\.jpeg\OpenWithProgids"; ValueType: string; ValueName: "EditorFotos3x4.Image"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associateimages
Root: HKCU; Subkey: "Software\Classes\.png\OpenWithProgids"; ValueType: string; ValueName: "EditorFotos3x4.Image"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associateimages
Root: HKCU; Subkey: "Software\Classes\.bmp\OpenWithProgids"; ValueType: string; ValueName: "EditorFotos3x4.Image"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associateimages

Root: HKCU; Subkey: "Software\Classes\EditorFotos3x4.Image"; ValueType: string; ValueName: ""; ValueData: "Imagem 3x4"; Flags: uninsdeletekey; Tasks: associateimages
Root: HKCU; Subkey: "Software\Classes\EditorFotos3x4.Image\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associateimages
Root: HKCU; Subkey: "Software\Classes\EditorFotos3x4.Image\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associateimages

; Info de instalação
Root: HKCU; Subkey: "Software\EditorFotos3x4"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\EditorFotos3x4"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\EditorFotos3x4"; ValueType: string; ValueName: "Architecture"; ValueData: "{code:GetArchitectureName}"; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\EditorFotos3x4"
Type: filesandordirs; Name: "{userappdata}\.editor_fotos_3x4"
Type: dirifempty; Name: "{app}"

[Code]
var
  IsX64System: Boolean;

function GetArchitectureName(Param: String): String;
begin
  if IsX64System then
    Result := 'x64'
  else
    Result := 'x86';
end;

function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  Result := True;
  
  GetWindowsVersionEx(Version);
  IsX64System := IsWin64;
  
  // Verificar requisitos mínimos
  if Version.Major < 10 then
  begin
    MsgBox('Este aplicativo requer Windows 10 ou superior.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Log de detecção de arquitetura
  Log('Sistema detectado: ' + GetArchitectureName(''));
  Log('Windows versao: ' + IntToStr(Version.Major) + '.' + IntToStr(Version.Minor));
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Verificar instalação
    if not FileExists(ExpandConstant('{app}\{#MyAppExeName}')) then
    begin
      MsgBox('ERRO: Arquivo principal não foi instalado corretamente.', mbError, MB_OK);
      Exit;
    end;
    
    // Verificar componentes críticos
    if not DirExists(ExpandConstant('{app}\_internal')) then
    begin
      MsgBox('AVISO: Alguns componentes podem estar faltando.', mbInformation, MB_OK);
    end;
  end;
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo,
  MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var
  S: String;
begin
  S := '';
  
  if MemoDirInfo <> '' then
    S := S + MemoDirInfo + NewLine + NewLine;
  
  if MemoGroupInfo <> '' then
    S := S + MemoGroupInfo + NewLine + NewLine;
    
  if MemoTasksInfo <> '' then
    S := S + MemoTasksInfo + NewLine + NewLine;
  
  S := S + 'Arquitetura do sistema: ' + GetArchitectureName('') + NewLine;
  
  Result := S;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Limpar configurações do usuário (opcional)
    if MsgBox('Deseja remover as configurações do aplicativo?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      RegDeleteKeyIncludingSubkeys(HKCU, 'Software\EditorFotos3x4');
      DelTree(ExpandConstant('{userappdata}\EditorFotos3x4'), True, True, True);
    end;
  end;
end;
