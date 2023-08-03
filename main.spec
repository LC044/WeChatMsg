# -*- mode: python ; coding: utf-8 -*-

add_files = [
    ("D:\\Project\\Python\\WeChatMsg\\app\\data\\icon.png",'.\\app\\data'),
    ("D:\\Project\\Python\\WeChatMsg\\app\\data\\stopwords.txt",'.\\app\\data'),
    ("D:\\Project\\Python\\WeChatMsg\\app\\data\\bg.gif",'.\\app\\data'),
    ("D:\\Project\\Python\\WeChatMsg\\app\\ImageBox",'.\\app\\ImageBox'),
    ("D:\\Project\\Python\\WeChatMsg\\app\\DataBase",'.\\app\\DataBase'),
    #("D:\\Project\\Python\\WeChatMsg\\app\\Ui",'.\\app\\Ui'),
    ("D:\\Project\\Python\\WeChatMsg\\sqlcipher-3.0.1",'.\\sqlcipher-3.0.1'),
    ('.\\resource\\datasets', 'pyecharts\\datasets\\.'),
    ('.\\resource\\render\\templates', 'pyecharts\\render\\templates\\.'),
    ('.\\data\\AnnualReport', 'data\\AnnualReport')
]
block_cipher = None

#("D:\\Project\\Python\\WeChatMsg\\sqlcipher-3.0.1",'.\\sqlcipher-3.0.1')

a = Analysis(
    ['main.py',
    './app/DataBase/data.py','./app/DataBase/output.py',
    './app/Ui/mainview.py','./app/Ui/mainwindow.py',
    './app/Ui/__init__.py',
    './app/Ui/chat/chat.py','./app/Ui/chat/chatUi.py',
    './app/Ui/contact/contact.py','./app/Ui/contact/contactUi.py','./app/Ui/contact/analysis/analysis.py','./app/Ui/contact/analysis/charts.py','./app/Ui/contact/report/report.py',
    './app/Ui/contact/userinfo/userinfoUi.py',
    './app/Ui/decrypt/decrypt.py','./app/Ui/decrypt/decryptUi.py',
    './app/Ui/userinfo/userinfo.py','./app/Ui/userinfo/userinfoUi.py',
    ],
    pathex=[],
    binaries=[],
    datas=add_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./app/data/icon.png'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
