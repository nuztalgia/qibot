from lib.characters.greeter import Greeter as _Greeter
from lib.characters.overseer import Overseer as _Overseer
from lib.characters.reporter import Reporter as _Reporter

Greeter = _Greeter()
Overseer = _Overseer()
Reporter = _Reporter()

__all__ = [
    "Greeter",
    "Overseer",
    "Reporter",
]
