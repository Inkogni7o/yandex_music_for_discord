from PyInstaller.utils.hooks import collect_submodules


hidden_imports = collect_submodules("winrt")

analysis = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("src/app/static/label.png", "src/app/static"),
        ("src/app/static/theme.qss", "src/app/static"),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="YandexMusicRPC",
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
