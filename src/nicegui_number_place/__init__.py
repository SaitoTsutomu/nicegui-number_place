"""nicegui_number_place"""

from importlib.metadata import metadata

from .number_place import Game, main

_package_metadata = metadata(str(__package__))
__version__ = _package_metadata["Version"]
__author__ = _package_metadata.get("Author-email", "")

__all__ = ["Game", "__author__", "__version__", "main"]
