# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para Editor de Fotos 3x4
CORRIGIDO: Caminhos ajustados e haarcascade incluído
"""

import os
import sys
from pathlib import Path

# Diretório base do projeto (onde está o .spec = src/)
base_dir = Path(SPECPATH)
# Diretório raiz do projeto (acima de src/)
root_dir = base_dir.parent

print(f"DEBUG: base_dir = {base_dir}")
print(f"DEBUG: root_dir = {root_dir}")

# Caminhos para DLLs C# (relativo a src/)
cs_dlls_x64 = base_dir / "modules" / "cs_dlls" / "x64"
cs_dlls_x86 = base_dir / "modules" / "cs_dlls" / "x86"

# Coleta DLLs C#
cs_binaries = []
cs_datas = []

# Incluir DLLs x64 e x86
for arch_dir, arch_name in [(cs_dlls_x64, "x64"), (cs_dlls_x86, "x86")]:
    if arch_dir.exists():
        print(f"DEBUG: Incluindo DLLs {arch_name} de {arch_dir}")
        for dll_file in arch_dir.glob("*.dll"):
            cs_binaries.append((str(dll_file), f"cs_dlls/{arch_name}"))
        for exe_file in arch_dir.glob("*.exe"):
            cs_binaries.append((str(exe_file), f"cs_dlls/{arch_name}"))
        for json_file in arch_dir.glob("*.json"):
            cs_datas.append((str(json_file), f"cs_dlls/{arch_name}"))

# Haarcascade (CORRIGIDO: buscar na raiz)
haarcascade_path = root_dir / 'haarcascade_frontalface_default.xml'
if not haarcascade_path.exists():
    print(f"AVISO: haarcascade não encontrado em {haarcascade_path}")
    # Tentar em src/
    haarcascade_path = base_dir / 'haarcascade_frontalface_default.xml'
    if not haarcascade_path.exists():
        print("ERRO: haarcascade_frontalface_default.xml não encontrado!")
    else:
        print(f"DEBUG: haarcascade encontrado em {haarcascade_path}")
else:
    print(f"DEBUG: haarcascade encontrado em {haarcascade_path}")

# Dados adicionais (CORRIGIDO)
additional_datas = []

# Incluir haarcascade se encontrado
if haarcascade_path.exists():
    additional_datas.append((str(haarcascade_path), '.'))

# Incluir módulos Python (CORRIGIDO: caminho relativo a base_dir)
modules_dir = base_dir / 'modules'
if modules_dir.exists():
    additional_datas.append((str(modules_dir), 'modules'))
    print(f"DEBUG: Incluindo modules de {modules_dir}")

# Combinar todos os dados
all_datas = additional_datas + cs_datas

print(f"DEBUG: Total de {len(all_datas)} arquivos de dados incluídos")
print(f"DEBUG: Total de {len(cs_binaries)} binários incluídos")

# Imports ocultos necessários
hidden_imports = [
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'customtkinter',
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageEnhance',
    'PIL.ImageOps',
    'subprocess',
    'json',
    'pathlib',
    'modules.cs_bridge',
    'modules.face_detection',
    'modules.file_manager',
    'modules.gui_components',
    'modules.image_processing',
    'modules.image_processing_hybrid',
    'modules.utils',
	'modules.config_manager',
	'modules.logger',
]

a = Analysis(
    ['main.py'],
    pathex=[str(base_dir)],
    binaries=cs_binaries,
    datas=all_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy', 'pandas', 'jupyter', 'IPython', 
        'notebook', 'pytest', 'sphinx',
        'tkinter.test', 'unittest',
        'pydoc', 'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicatas
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Configuração do executável
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Editor_fotos_3x4',
    icon=str(root_dir / 'icon.ico') if (root_dir / 'icon.ico').exists() else None,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Interface gráfica
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Coleta todos os arquivos em uma pasta
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='editor_fotos'
)

print("=" * 60)
print("SPEC EXECUTADO COM SUCESSO")
print("=" * 60)
