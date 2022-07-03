from asyncio import sleep

from discord import Bot, Cog, Member

from lib.characters import Characters
from lib.common import Utils
from lib.logger import Log


class MemberEvents(Cog):
    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        Log.i(f"{Utils.get_member_nametag(member)} has joined the server.")
        await Characters.report_member_joined(member)
        await sleep(1)  # Wait until after Discord's default welcome message is sent.
        await Characters.greet(member)

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        Log.i(f"{Utils.get_member_nametag(member)} has left the server.")
        await Characters.report_member_left(member)

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.display_name != after.display_name:
            Log.i(f"{Utils.get_member_nametag(after)} has changed their display name.")
            await Characters.report_member_renamed(after, before.display_name)


def setup(bot: Bot) -> None:
    bot.add_cog(MemberEvents(bot))
