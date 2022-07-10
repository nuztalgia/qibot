import re
import string
from typing import Callable, Final

_TEMPLATE_KEY_PATTERN: Final[re.Pattern] = re.compile(r"\${?(\w*)", re.ASCII)


def get_template_keys(template_string: str) -> set[str]:
    return set(_TEMPLATE_KEY_PATTERN.findall(template_string))


class Template(string.Template):
    sub: Final[Callable[..., str]] = string.Template.substitute
    safe_sub: Final[Callable[..., str]] = string.Template.safe_substitute
