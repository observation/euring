from importlib import metadata

try:
    __version__ = metadata.version("euring")
except metadata.PackageNotFoundError:
    __version__ = "0+unknown"
