# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['SoilWise/main.py'],  # IMPORTANT: Entry point is SoilWise/main.py
    pathex=[],
    binaries=[],
    datas=[
        # Include all your assets
        ('SoilWise/assets/images/*', 'SoilWise/assets/images'),
        
        # Include database files from root
        ('database/*', 'database'),
        
        # Include knowledge base from root
        ('knowledge_base/*', 'knowledge_base'),
        
        # Include data files from root
        ('data/*', 'data'),
        
        # Include any JSON/config files in SoilWise
        ('SoilWise/config/*', 'SoilWise/config'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        'firebase_admin',
        'geopandas',
        'pandas',
        'sqlalchemy',
        'psycopg2',
        'shapely',
        'fiona',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SoilWise',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='SoilWise/assets/images/sample3.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SoilWise',
)
