"""Top-level package for the Privacy Sandbox application."""

from importlib import metadata

try:
    __version__ = metadata.version("privacy-sandbox")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"

__all__ = ["__version__"]

