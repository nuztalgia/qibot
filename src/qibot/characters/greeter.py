from discord import Member

from qibot.characters.core import Action, Character
from qibot.utils import BotChannel


class Greeter(Character):
    async def greet(self, member: Member) -> None:
        welcome_text = self._get_dialogue(Action.MEMBER_JOINED, name=member.mention)
        rules_text = self._get_dialogue(Action.MENTION_RULES, url=BotChannel.RULES.url)
        await self._send_message(
            action=Action.MEMBER_JOINED,
            destination=BotChannel.WELCOME,
            text=f"{welcome_text}\n\n{rules_text}",
        )
