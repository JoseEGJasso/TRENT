# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
	("fonts", "fonts")
]

a = Analysis(['src/trent_ui.py'],
             pathex=['/home/josejasso2000/Escritorio/PDI-20212/TRENT'],
             binaries=[],
             datas=added_files,
             hiddenimports=['PIL.Image', 'numpy', 'PIL.ImageDraw', 'PIL.ImageFont'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TRENT',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
