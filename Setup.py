from cx_Freeze import setup, Executable

setup(
    name="Aurora NATs injector",
    version="2.0",
    author="IVAO - OCC",
    description="Aurora NATs injector",
    executables = [
        Executable("D:/Perfil/Documents/Proyectos/nat-updater/nat.py")
    ]
)