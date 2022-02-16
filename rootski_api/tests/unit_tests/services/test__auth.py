from time import time

TEST_EMAIL = "test@unit-tests.com"
KEY_ID = "vBU9jC18VYmhB09UOHVOChs9A15t/8+2TvAJkR6+gjk="
COGNITO_ALGORITHM = "RS256"
COGNITO_ID_TOKEN_HEADER = {"kid": KEY_ID, "alg": COGNITO_ALGORITHM}
COGNITO_ID_TOKEN_PAYLOAD = {
    "at_hash": "NuFOjWS_EP1Ow3ytv3RZ0A",
    "sub": "d0c3972c-0b0f-4177-8cfb-636a17331505",
    "cognito:groups": ["us-west-2_NMATFlcVJ_Google"],
    "email_verified": False,
    "iss": "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_NMATFlcVJ",
    "cognito:username": "Google_114163402210963774138",
    "origin_jti": "3b564b56-5d4f-46f2-80f3-3a2c489b9033",
    "aud": "35ufe1nk2tasug2gmbl5l9mra3",  # this is a web client ID
    "identities": [
        {
            "userId": "114163402210963774138",
            "providerName": "Google",
            "providerType": "Google",
            "issuer": None,
            "primary": "true",
            "dateCreated": "1627180752091",
        }
    ],
    "token_use": "id",
    "auth_time": time(),
    "exp": time() + 60,  # will expire 20 seconds after this file is imported
    "iat": time(),
    "jti": "425fb09c-293d-42e5-9490-7b98d1ae6013",
    "email": TEST_EMAIL,
}
