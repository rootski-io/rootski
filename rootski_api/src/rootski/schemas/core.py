from pydantic import BaseModel

from rootski.services.auth import AuthService
from rootski.services.database import DBService
from rootski.services.logger import LoggingService


class Services(BaseModel):
    auth: AuthService
    db: DBService
    logger: LoggingService

    class Config:
        # allow members of Services to have types that are not pydantic schemas
        arbitrary_types_allowed = True


class HTTPError(BaseModel):
    detail: str
