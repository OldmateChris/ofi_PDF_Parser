import shutil

def is_installed(cmd: str) -> bool:
    return shutil.which(cmd) is not None
