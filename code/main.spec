# -*- mode: python ; coding: utf-8 -*-

import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/leoca/AppData/Local/Programs/Python/Python311/Lib/site-packages/satellite_tle', 'satellite_tle'), ('C:/Users/leoca/AppData/Local/Programs/Python/Python311/Lib/site-packages/itur', 'itur'),('C:/Users/leoca/AppData/Local/Programs/Python/Python311/Lib/site-packages/cartopy', 'cartopy')],
    hiddenimports=['babel.numbers', 'satellite_tle', 'itur', 'cartopy'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
