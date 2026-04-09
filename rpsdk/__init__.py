"""Shim package exposing the tournament SDK as `import rpsdk`."""

from rps_client.rpsdk import *  # noqa: F401,F403

__all__ = [name for name in globals().keys() if not name.startswith("_")]
