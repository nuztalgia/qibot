from asyncio import sleep
from typing import Final

from discord import Bot, Cog, Member

from lib.characters import BOUNCER, SANDY
from lib.logger import Log


class Salutations(Cog):
    """Handles actions to be executed when a member leaves/joins the server."""

    def __init__(self, bot: Bot) -> None:
        self.bot: Final[Bot] = bot

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        Log.i(f"{member.name}#{member.discriminator} has joined the server.")
        await BOUNCER.announce_member_joined(self.bot, member)
        await sleep(1)  # Wait until after Discord's default welcome message is sent.
        await SANDY.greet(self.bot, member)

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        Log.i(f"{member.name}#{member.discriminator} has left the server.")
        await BOUNCER.announce_member_left(self.bot, member)


def setup(bot: Bot) -> None:
    bot.add_cog(Salutations(bot))
