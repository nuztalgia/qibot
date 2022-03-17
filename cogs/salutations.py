from typing import Final

from discord import Bot, Cog, Member


class Salutations(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Final[Bot] = bot

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        channel = member.guild.system_channel
        await channel.send(f"Well well well... you made it, {member.mention}.")


def setup(bot: Bot) -> None:
    bot.add_cog(Salutations(bot))
