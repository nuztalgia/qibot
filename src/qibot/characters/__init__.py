from qibot.characters.greeter import Greeter as _Greeter
from qibot.characters.overseer import Overseer as _Overseer
from qibot.characters.reporter import Reporter as _Reporter

Greeter = _Greeter()
Overseer = _Overseer()
Reporter = _Reporter()

__all__ = [
    "Greeter",
    "Overseer",
    "Reporter",
]
