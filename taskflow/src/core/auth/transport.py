from fastapi_users.authentication import (
    BearerTransport,
    CookieTransport,
)

from src.core import settings

bearer_transport = BearerTransport(
    tokenUrl=settings.api.bearer_token_url,
)
cookie_transport = CookieTransport(
    cookie_max_age=settings.access_token.lifetime_seconds,
    cookie_secure=False,
)