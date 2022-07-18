from enum import Enum, unique
from typing import Callable, Final, TypeAlias

from colorama import Fore, Style

_ColorText: TypeAlias = Callable[[str], str]
_ColorPrint: TypeAlias = Callable[[str], None]


@unique
class _Color(Enum):
    CYAN = Fore.CYAN
    GREEN = Fore.GREEN
    GREY = Fore.BLACK  # "Bright black" shows up as grey.
    MAGENTA = Fore.MAGENTA
    RED = Fore.RED
    YELLOW = Fore.YELLOW

    def color_text(self, text: str) -> str:
        return f"{self.value}{Style.BRIGHT}{text}{Style.NORMAL}{Fore.RESET}"

    def color_print(self, text: str) -> None:
        print(self.color_text(text))


cyan: Final[_ColorText] = _Color.CYAN.color_text
green: Final[_ColorText] = _Color.GREEN.color_text
grey: Final[_ColorText] = _Color.GREY.color_text
magenta: Final[_ColorText] = _Color.MAGENTA.color_text
red: Final[_ColorText] = _Color.RED.color_text
yellow: Final[_ColorText] = _Color.YELLOW.color_text

print_cyan: Final[_ColorPrint] = _Color.CYAN.color_print
print_green: Final[_ColorPrint] = _Color.GREEN.color_print
print_grey: Final[_ColorPrint] = _Color.GREY.color_print
print_magenta: Final[_ColorPrint] = _Color.MAGENTA.color_print
print_red: Final[_ColorPrint] = _Color.RED.color_print
print_yellow: Final[_ColorPrint] = _Color.YELLOW.color_print
