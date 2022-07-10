from asyncio import sleep

from discord import Cog, Member

from qibot.characters import Greeter, Reporter
from qibot.utils import Log, get_member_nametag


class MemberListeners(Cog):
    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        Log.i(f"{get_member_nametag(member)} has joined the server.")
        await Reporter.report_member_joined(member)
        await sleep(1)  # Wait until after Discord's default welcome message is sent.
        await Greeter.greet(member)

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        Log.i(f"{get_member_nametag(member)} has left the server.")
        await Reporter.report_member_left(member)

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.display_name != after.display_name:
            Log.i(f"{get_member_nametag(after)} has changed their display name.")
            await Reporter.report_member_renamed(after, before.display_name)
