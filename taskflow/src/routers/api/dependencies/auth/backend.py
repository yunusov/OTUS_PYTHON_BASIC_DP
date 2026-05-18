from fastapi_users.authentication import AuthenticationBackend

from src.core.auth.transport import bearer_transport
from .strategy import get_database_strategy

authentification_backend = AuthenticationBackend(
    name="access-token-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
