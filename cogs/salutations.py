from asyncio import sleep
from typing import Final, Optional

from discord import Bot, Cog, Member, Webhook

from lib.channels import Channel
from lib.characters import Action, Character
from lib.logger import Log


class Salutations(Cog):
    """Handles actions to be executed when a member leaves/joins the server."""

    def __init__(self, bot: Bot) -> None:
        self.bot: Final[Bot] = bot
        self._welcome_webhook: Optional[Webhook] = None
        self._logging_webhook: Optional[Webhook] = None

    @Cog.listener()
    async def on_ready(self) -> None:
        self._welcome_webhook = await Channel.WELCOME.get_webhook(self.bot)
        self._logging_webhook = await Channel.LOGGING.get_webhook(self.bot)

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        Log.i(f"{member.name}#{member.discriminator} has joined the server.")
        await self._bouncer_salute(Action.MEMBER_JOINED, member, emoji="✨")
        await sleep(1)  # Wait until after Discord's default welcome message is sent.
        await Character.SANDY.handle(
            action=Action.MEMBER_JOINED,
            webhook=self._welcome_webhook,
            name=member.mention,
        )

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        Log.i(f"{member.name}#{member.discriminator} has left the server.")
        await self._bouncer_salute(Action.MEMBER_LEFT, member, emoji="💨")

    async def _bouncer_salute(self, action: Action, member: Member, emoji: str) -> None:
        await Character.BOUNCER.handle(
            action, webhook=self._logging_webhook, name=member.mention, emoji=emoji
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Salutations(bot))
