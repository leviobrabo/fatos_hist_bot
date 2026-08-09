from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PACKAGE_DIR / 'data'
ASSETS_DIR = PACKAGE_DIR / 'assets'


def data_path(filename: str) -> Path:
    return DATA_DIR / filename


def asset_path(filename: str) -> Path:
    return ASSETS_DIR / filename
