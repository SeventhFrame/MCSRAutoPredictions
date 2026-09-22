# PyInstaller spec for the console-visible local browser app.
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("flask")

a = Analysis(
    ["python/app.py"],
    pathex=["python"],
    binaries=[],
    datas=[("python/templates", "templates")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AutoPredictions",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
