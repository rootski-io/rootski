from __future__ import annotations

from abc import ABC

from rootski.config.config import Config


class Service(ABC):
    def __init__(self, **kwargs):
        raise NotImplementedError("This class is abstract, breh!")

    def init(self, **kwargs):
        raise NotImplementedError("This class is abstract, breh!")

    @classmethod
    def from_config(cls, config: Config) -> Service:
        raise NotImplementedError("This class is abstract, breh!")
