from rootski.config.config import Config
from rootski.services.service import Service


class MockService(Service):
    def __init__(self, **kwargs):
        """This mock can stand in for any service."""

    def init(self):
        print("Initializing service!")

    @classmethod
    def from_config(cls, config: Config):
        return cls(dummy_param=config.host)
