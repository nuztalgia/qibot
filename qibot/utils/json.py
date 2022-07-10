import json
from typing import Any, Final

from qibot.assets import DATA_PATH
from qibot.utils.templates import Template

_JSON_FILE: Final[Template] = Template("${filename}.json")


def load_dict_from_file(filename: str, lowercase_keys: bool = True) -> dict[str, Any]:
    file_path = DATA_PATH / _JSON_FILE.sub(filename=filename)
    with file_path.open(mode="r", encoding="utf-8") as file:
        result = json.load(file)
    return _lowercase_keys(result) if lowercase_keys else result


def _lowercase_keys(original: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for key, value in original.items():
        new_value = _lowercase_keys(value) if isinstance(value, dict) else value
        result[key.lower()] = new_value
    return result
