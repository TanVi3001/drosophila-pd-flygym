"""Drosophila PD FlyGym computational research package."""

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("drosophila-pd-flygym")
except PackageNotFoundError:  # Source checkouts before editable installation.
    __version__ = "0+unknown"


__all__ = ["__version__"]
