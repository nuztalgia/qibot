from discord import Member

from lib.channels import Channel
from lib.characters.internal import Action, Character
from lib.common import Utils
from lib.embeds import FieldData
from lib.images import ImageUtils


def _get_core_member_fields(member: Member) -> list[FieldData]:
    return [
        FieldData("❄", "Unique ID", str(member.id), True),
        FieldData("🏷️", "Current Tag", Utils.get_member_nametag(member), True),
        FieldData(inline=True),  # Force any extra fields to start on the next row.
    ]


class Reporter(Character):
    async def report_member_joined(self, member: Member) -> None:
        fields = _get_core_member_fields(member) + [
            FieldData("🐣", "Account Created", Utils.format_time(member.created_at)),
        ]
        await self._report_member_action(member, Action.MEMBER_JOINED, fields)

    async def report_member_left(self, member: Member) -> None:
        fields = _get_core_member_fields(member) + [
            FieldData("🌱", "Joined Server", Utils.format_time(member.joined_at)),
            FieldData("🍂", "Server Roles", [role.mention for role in member.roles[1:]]),
        ]
        await self._report_member_action(member, Action.MEMBER_LEFT, fields)

    async def report_member_renamed(self, member: Member, old_name: str) -> None:
        fields = [
            FieldData("🌘", "Old Name", old_name, True),
            FieldData("🌔", "New Name", member.display_name, True),
            FieldData(inline=True),  # Blank field to properly align with common fields.
        ]
        await self._report_member_action(member, Action.MEMBER_RENAMED, fields)

    async def _report_member_action(
        self, member: Member, action: Action, fields: list[FieldData]
    ) -> None:
        await self._send_message(
            action=action,
            destination=Channel.ADMIN_LOG,
            text=f"**{self._get_dialogue(action, name=member.mention)}**",
            thumbnail=await ImageUtils.get_member_avatar(member),
            fields=fields,
        )
