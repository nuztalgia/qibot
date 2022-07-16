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

    def get_file(self) -> Optional[Path]:
        return self.value if self.value.is_file() else None


def get_token_file(force_prod: bool, msg_prefix: str = "\n") -> Optional[Path]:
    dev_file = _Token.DEV.get_file()
    prod_file = _Token.PROD.get_file()

    if not (dev_file or prod_file):
        print(f"{msg_prefix}You currently don't have any saved bot tokens.")
    elif force_prod and not prod_file:
        print(f"{msg_prefix}You currently don't have a saved bot token for production.")
    else:
        # Use prod if -p was specified, otherwise try to use dev (with prod as backup).
        return prod_file if force_prod else (dev_file or prod_file)

    return None
