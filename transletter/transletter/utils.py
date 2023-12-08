import json
from pathlib import Path

__all__ = ("get_available_langs",)


def get_available_langs():
    with Path("langs/langs.json").open() as file:
        data = json.load(file)

    choices = [(item["code"], item["name"]) for item in data]

    return tuple(choices)
