"""
Logic for authenticating incoming requests.

The code heavily borrows from this article:
https://gntrm.medium.com/jwt-authentication-with-fastapi-and-aws-cognito-1333f7f2729e
"""
from typing import List, Optional

import httpx
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
from loguru import logger
from pydantic import BaseModel

from rootski.config.config import ANON_USER, Config
from rootski.errors import AuthServiceError
from rootski.services.service import Service


class JsonWebKey(BaseModel):
    """
    Learn about Cognito JWKs here:
    https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html
    """

    kid: str  # key ID
    kty: str

    class Config:
        extra = "allow"


class JsonWebKeySet(BaseModel):
    keys: List[JsonWebKey]

    class Config:
        extra = "allow"


class AuthService(Service):
    _jwks: Optional[JsonWebKeySet] = None

    @classmethod
    def from_config(cls, config: Config):
        return cls(cognito_public_keys_url=config.cognito_public_keys_url)

    def __init__(self, cognito_public_keys_url: str):
        """Abstraction layer around verifying tokens."""
        self.__cognito_public_keys_url = cognito_public_keys_url

    def init(self):
        logger.info("Fetching Cognito Keys")
        self._jwks = get_jwks(self.__cognito_public_keys_url)
        logger.info(f"Fetched these keys: {str(self._jwks.json())}")

    def token_is_valid(self, token: str) -> bool:
        if not self._jwks:
            raise AuthServiceError("The auth service is not initialized. Did you call .init()?")
        if not token_is_well_formed(token=token):
            return False
        logger.info(f"Validating token: {token}")
        return jwt_is_valid(token, self._jwks)

    def get_token_email(self, token: str) -> Optional[str]:
        """Retrieve the email from the token, or return the anonymous user."""
        logger.info(f"token {token}")
        if not token_is_well_formed(token):
            error_msg = (
                f"Got this error while getting the 'email' from the JWT token {str(e)}"
                + f"\n\nToken: {str(token)}"
            )
            logger.error(error_msg)
            raise AuthServiceError("Error, JWT token is not wellformed. See logs for details.")
        return jwt.get_unverified_claims(token).get("email", ANON_USER)


def token_is_well_formed(token: str) -> bool:
    """Return ``True`` if the token can be decoded without verifying the signature."""
    try:
        jwt.get_unverified_claims(token)
        jwt.get_unverified_headers(token)
    except JWTError:
        return False
    return True


def get_jwks(jwk_url: str) -> JsonWebKeySet:
    response = httpx.get(jwk_url)
    return JsonWebKeySet(**response.json())


def get_token_jwk(token: str, jwks: JsonWebKeySet) -> Optional[JsonWebKey]:
    """Return the Cognito public key whose ID matches the key ID in the token header.

    If our Cognito user pool does not have a matching key, return ``None``... we're
    not going to be able to authenticate this token. :(

    Args:
        token: JWT token from the header of an incoming request
        jwks: Json Web Keys corresponding to our Cognito user pool
    """
    try:
        token_kid = jwt.get_unverified_header(token).get("kid")
    except JWTError as e:
        logger.error(f"Got this error while getting the email from the JWT token {str(e)}")
        raise AuthServiceError("Error while getting email from JWT claims. See logs for details.")
    for key in jwks.keys:
        if key.kid == token_kid:
            return key


def jwt_is_valid(token: str, jwks: JsonWebKeySet) -> bool:
    """Return ``True`` if the jwt ``token`` was signed by our Cognito user pool identity server."""
    token_jwk: Optional[JsonWebKey] = get_token_jwk(token, jwks)

    if not token_jwk:
        raise AuthServiceError(
            "No public key found! Did you call AuthService.init()? Are the Cognito config values right?"
        )

    hmac_key = jwk.construct(token_jwk.dict())

    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    return hmac_key.verify(message.encode(), decoded_signature)
