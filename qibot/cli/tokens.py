import shutil
from enum import Enum, auto, unique
from pathlib import Path
from typing import Optional


@unique
class _Token(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, values: list) -> Path:
        value = Path(__file__).parent / f".{name}.key"
        if value.is_dir():
            shutil.rmtree(value)
        return value

    DEV = auto()
    PROD = auto()

    @classmethod
    def get_files(cls) -> tuple[Optional[Path], ...]:
        return tuple(member._get_file() for member in cls)

    def _get_file(self) -> Optional[Path]:
        return self.value if self.value.is_file() else None


def get_token_file(prod: bool) -> Optional[Path]:
    dev_file, prod_file = _Token.get_files()

    if not (dev_file or prod_file):
        print("\nYou currently don't have any saved bot tokens.")
    elif prod and not prod_file:
        print("\nYou currently don't have a saved bot token for production.")
    else:
        # Use prod if -p was specified, otherwise try to use dev (with prod as backup).
        return prod_file if prod else (dev_file or prod_file)

    return None
