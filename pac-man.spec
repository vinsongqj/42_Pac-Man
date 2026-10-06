# pac-man.spec
a = Analysis(
    ['pac-man.py'],
    pathex=['.'],
    datas=[('assets', 'assets'), ('config.json', '.')],
    hiddenimports=['mazegenerator'],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='pac-man',
    console=True,
)