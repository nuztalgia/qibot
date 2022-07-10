from pathlib import Path
from typing import Final

_ASSETS_DIR_PATH: Final[Path] = Path(__file__).parent

DATA_PATH: Final[Path] = _ASSETS_DIR_PATH / "data"
IMAGE_PATH: Final[Path] = _ASSETS_DIR_PATH / "images"
