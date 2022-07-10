import json
from typing import Any, Final

from qibot.utils.templates import Template

_JSON_FILE_PATH: Final[Template] = Template("${path}/${name}.json")


def load_json_from_file(
    filename: str, path: str = "assets/data/", lowercase_keys: bool = True
) -> dict[str, Any]:
    full_path = _JSON_FILE_PATH.sub(path=path, name=filename)
    with open(full_path, mode="r", encoding="utf-8") as file:
        result = json.load(file)
    return _lowercase_keys(result) if lowercase_keys else result


def _lowercase_keys(original: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for key, value in original.items():
        new_value = _lowercase_keys(value) if isinstance(value, dict) else value
        result[key.lower()] = new_value
    return result
