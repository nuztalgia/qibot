from asyncio import sleep
from typing import Final

from discord import Bot, Cog, Member

from lib.characters import Action, Character
from lib.common import Constants
from lib.logger import Log


class Salutations(Cog):
    """Handles actions to be executed when a member leaves/joins the server."""

    def __init__(self, bot: Bot) -> None:
        self.bot: Final[Bot] = bot

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        Log.i(f'{member.name}#{member.discriminator} joined "{member.guild.name}".')
        await self._bouncer_salute(Action.MEMBER_JOINED, member)
        await sleep(1)  # Wait until after Discord's default welcome message is sent.
        await Character.SANDY.handle(
            Action.MEMBER_JOINED, member.guild.system_channel, name=member.mention
        )

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        Log.i(f'{member.name}#{member.discriminator} left "{member.guild.name}".')
        await self._bouncer_salute(Action.MEMBER_LEFT, member)

    async def _bouncer_salute(self, action: Action, member: Member) -> None:
        channel = await self.bot.fetch_channel(Constants.SALUTATIONS_CHANNEL_ID)
        if channel:
            await Character.BOUNCER.handle(
                action, channel, name=member.mention, allowed_mentions=False
            )
        else:
            Log.w("  The salutations channel ID is not configured correctly.")


def setup(bot: Bot) -> None:
    bot.add_cog(Salutations(bot))
