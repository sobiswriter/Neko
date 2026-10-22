# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
import sys

# Keep unrelated tools' ICU and runtime DLLs out of the Windows bundle.
os.environ['PATH'] = os.pathsep.join([
    str(Path(sys.executable).parent),
    str(Path(os.environ['SystemRoot']) / 'System32'),
    os.environ['SystemRoot'],
])

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('neko_sleep.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DesktopNeko',
    icon='neko_sleep.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
