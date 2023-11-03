from .config import (
    WEIYI_API_BASE_URL,
    WEIYI_APP_ID,
    WEIYI_APP_KEY,
    WEIYI_BASE_URL,
    WEIYI_CIPHER,
    WEIYI_REDIRECT_URI,
    WEIYI_SCOPES,
)
from .main import WeiyiClient

__all__ = [
    "WeiyiClient",
    "weiyi_client",
]

weiyi_client = WeiyiClient(
    app_id=WEIYI_APP_ID,
    app_key=WEIYI_APP_KEY,
    cipher=WEIYI_CIPHER,
    scopes=WEIYI_SCOPES,
    redirect_uri=WEIYI_REDIRECT_URI,
    base_url=WEIYI_BASE_URL,
    api_base_url=WEIYI_API_BASE_URL,
)
