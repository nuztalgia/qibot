from typing import Any, Final, Optional

from lib.utils.json import load_json_from_file

_CONFIG: Final[dict[str, Any]] = load_json_from_file(filename="config", path=".")


class Config:
    BOT_TOKEN: Final[str] = _CONFIG["bot_token"]
    SERVER_ID: Final[int] = _CONFIG["server_id"]
    DEV_MODE_ENABLED: Final[bool] = _CONFIG.get("dev_mode_enabled", False)
    LOG_THRESHOLD: Final[Optional[str]] = _CONFIG.get("log_threshold")


def get_channel_id(channel_name: str) -> int:
    return _CONFIG["channel_ids"].get(channel_name.lower(), 0)
