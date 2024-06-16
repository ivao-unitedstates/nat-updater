from cx_Freeze import setup, Executable

setup(
    name="Aurora NAT Updater",
    version="2.0",
    author="IVAO - OCC",
    description="Aurora NATs injector",
    executables = [
        Executable(
            "./nat.py",
            icon="./OCC.ico",
        )
    ]
)