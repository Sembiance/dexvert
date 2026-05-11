from importlib import metadata
get_version = lambda : metadata.version("binwalk")

__version__ = get_version()
