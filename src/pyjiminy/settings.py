# -*- coding: utf-8 -*-
try:
    import dotenv
except ImportError:
    dotenv = None
import click
import os

def load_dotenv(path: str=None) -> bool:
    """Load "dotenv" files in order of precedence to set environment variables.
    If an env var is already set it is not overwritten, so earlier files in the
    list are preferred over later files.
    This is a no-op if `python-dotenv`_ is not installed.
    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme
    :param path: Load the file at this location instead of searching.
    :return: ``True`` if a file was loaded.
    """
    if dotenv is None:
        if path or os.path.isfile(".env") or os.path.isfile(".pyjiminyenv"):
            click.secho(
                " * Tip: There are .env or .pyjiminyenv files present."
                ' Do "pip install python-dotenv" to use them.',
                fg="yellow",
                err=True,
            )

        return False

    # if the given path specifies the actual file then return True,
    # else False
    if path is not None:
        if os.path.isfile(path):
            return dotenv.load_dotenv(path, encoding="utf-8")

        return False

    new_dir = None

    for name in (".env", ".pyjiminyenv"):
        path = dotenv.find_dotenv(name, usecwd=True)

        if not path:
            continue

        if new_dir is None:
            new_dir = os.path.dirname(path)

        dotenv.load_dotenv(path, encoding="utf-8")

    return new_dir is not None  # at least one file was located and loaded


PASSWORD = os.environ.get("PYJIMINY_GMAIL_APP_PASSWORD")
FROM_ADDRESS = os.environ.get("PYJIMINY_GMAIL_FROM_ADDRESS")
TO_ADDRESS = os.environ.get("PYJIMINY_GMAIL_TO_ADDRESS")


HOTEL = os.environ.get("PYJIMINY_HOTEL_NAME")
YEAR  = os.environ.get("PYJIMINY_HOTEL_ARRIVAL_YEAR")
MONTH = os.environ.get("PYJIMINY_HOTEL_ARRIVAL_MONTH")
DAY = os.environ.get("PYJIMINY_HOTEL_ARRIVAL_DAY")
NIGHTS = os.environ.get("PYJIMINY_HOTEL_STAY_NIGHTS")
ROOMS = os.environ.get("PYJIMINY_HOTEL_ROOM_NUMBERS")
ADULTS = os.environ.get("PYJIMINY_HOTEL_ADULT_NUMBERS")