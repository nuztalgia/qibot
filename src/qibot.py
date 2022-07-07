from typing import Final, Optional

from discord import Activity, ActivityType, Bot

from lib.channels import Channel
from lib.characters import Characters
from lib.logger import Log


class QiBot(Bot):
    VERSION: Final[str] = "0.1.0"

    async def on_ready(self) -> None:
        Log.i(f'  Successfully logged in as "{self.user}".')

        server_name = self._get_server_name()
        if not server_name:
            return await self.close()

        Log.i(f'Monitoring server: "{server_name}"')

        await Channel.initialize_all(self)
        await Characters.initialize()

        await self.change_presence(
            activity=Activity(type=ActivityType.watching, name="everything.")
        )

    def _get_server_name(self) -> Optional[str]:
        if len(self.guilds) != 1:
            Log.e(
                f"This bot account is a member of {len(self.guilds)} servers."
                f"{Log.NEWLINE}It must be present in exactly 1 server. Exiting."
            )
            return None
        elif self.guilds[0].id != self.debug_guilds[0]:
            Log.e(
                f'This bot is running in an unexpected server: "{self.guilds[0].name}"'
                f"{Log.NEWLINE}Make sure the SERVER_ID is configured properly. Exiting."
            )
            return None
        else:
            return self.guilds[0].name
