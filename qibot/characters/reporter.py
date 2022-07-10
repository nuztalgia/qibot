from discord import Member

from qibot.characters.core import Action, Character
from qibot.embeds import Fields, create_inline_fields, create_standalone_fields
from qibot.utils import (
    BotChannel,
    format_time,
    get_member_avatar_file,
    get_member_nametag,
)


def _get_core_member_fields(member: Member) -> Fields:
    return create_inline_fields(
        ("❄", "Unique ID", str(member.id)),
        ("🏷️", "Current Tag", get_member_nametag(member)),
    )


class Reporter(Character):
    async def report_member_joined(self, member: Member) -> None:
        fields = _get_core_member_fields(member) + create_standalone_fields(
            ("🐣", "Account Created", format_time(member.created_at)),
        )
        await self._report_member_action(member, Action.MEMBER_JOINED, fields)

    async def report_member_left(self, member: Member) -> None:
        fields = _get_core_member_fields(member) + create_standalone_fields(
            ("🌱", "Joined Server", format_time(member.joined_at)),
            ("🍂", "Server Roles", [role.mention for role in member.roles[1:]]),
        )
        await self._report_member_action(member, Action.MEMBER_LEFT, fields)

    async def report_member_renamed(self, member: Member, old_name: str) -> None:
        fields = create_inline_fields(
            ("🌘", "Old Name", old_name),
            ("🌔", "New Name", member.display_name),
        )
        await self._report_member_action(member, Action.MEMBER_RENAMED, fields)

    async def _report_member_action(
        self, member: Member, action: Action, fields: Fields
    ) -> None:
        await self._send_message(
            action=action,
            destination=BotChannel.ADMIN_LOG,
            text=f"**{self._get_dialogue(action, name=member.mention)}**",
            thumbnail=await get_member_avatar_file(member),
            fields=fields,
        )
