from enum import Enum, auto, unique
from typing import Final

from lib.common import Template

_COG_MODULE_TEMPLATE: Final[Template] = Template("cogs.$name")


@unique
class CogRegistry(Enum):
    def __init__(self, cog_class_name: str, is_production_ready: bool = False) -> None:
        # An alias for "self.value" that makes more semantic sense.
        self.cog_class_name: Final[str] = cog_class_name
        # True for all "Production Cogs", and False for all "Development Cogs".
        self.is_production_ready: Final[bool] = is_production_ready

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, values: list) -> str:
        # Convert CONSTANT_CASE to PascalCase to get the name of the cog's class.
        return "".join(word.title() for word in name.split("_"))

    def get_module_name(self) -> str:
        return _COG_MODULE_TEMPLATE.substitute(name=self.name.lower())

    """ PRODUCTION COGS - The cogs listed here are functional and (mostly) bug-free. """
    # None yet!

    """ DEVELOPMENT COGS - The cogs listed here may be nonfunctional/unstable/buggy. """
    SALUTATIONS = auto()
