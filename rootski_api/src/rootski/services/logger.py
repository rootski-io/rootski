import sys

from loguru import logger

from rootski.config.config import Config, LogLevel
from rootski.services.service import Service


class LoggingService(Service):
    def __init__(self, log_level: LogLevel):
        self.log_level: LogLevel = log_level

    def init(self):
        # remove the default log handler and add a new one that only
        # handles logs up to the desired log level
        logger.remove()
        logger.add(sink=sys.stderr, level=self.log_level)
        logger.info(f"Initialized logger with level {self.log_level}")

    @classmethod
    def from_config(cls, config: Config):
        return cls(log_level=config.log_level)
