from typing import Union

from productizer.utils.Requester import fetch
from productizer.utils.settings import get_setting, if_test_mode
from pydantic import BaseModel


class AccessDeniedResponse(BaseModel):
    message: str


async def authorize(authorization_bearer_token: Union[str, None], authorization_provider: Union[str, None]) -> None:
    """
    Throws 401 if not authorized
    """
    if if_test_mode():
        return

    await fetch(
        {
            "url": f"{get_setting('AUTHORIZATION_GW_ENDPOINT_URL')}/auth/authorize",
            "method": "POST",
            "headers": {
                "Authorization": authorization_bearer_token,
                "X-Authorization-Provider": authorization_provider,
                "X-Authorization-Provider-Context": "testbed-test-productizer",
            },
        }
    )
