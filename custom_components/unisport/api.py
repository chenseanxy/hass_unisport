"""Sample API Client."""

from __future__ import annotations

import json
import re
import socket
from typing import TYPE_CHECKING

import aiohttp
import async_timeout

from .const import LOGGER
from .data import UnisportLocation

if TYPE_CHECKING:
    from typing import Any


class UnisportApiClientError(Exception):
    """Exception to indicate a general API error."""


class UnisportApiClientCommunicationError(
    UnisportApiClientError,
):
    """Exception to indicate a communication error."""


class UnisportApiClientAuthenticationError(
    UnisportApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise UnisportApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class UnisportApiClient:
    """Sample API Client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._session = session
        self._reg_locations = re.compile(r"const locations = (.*);")
        self._reg_validations = re.compile(r"const live_validations = (.*);")

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        text = await self._api_wrapper(
            method="get",
            url="https://oma.enkora.fi/unisport/populartimes",
            plain_response=True,
        )
        locations = self._reg_locations.search(text)
        live_validations = self._reg_validations.search(text)

        if locations is None or live_validations is None:
            msg = "Failed to parse locations or live validations"
            raise UnisportApiClientError(msg)

        locations = json.loads(locations.group(1))
        live_validations = json.loads(live_validations.group(1))
        LOGGER.debug("Got live_validations: %s", live_validations)
        LOGGER.debug("Got locations: %s", locations)
        if not live_validations:
            live_validations = {}
        return {
            "locations": {int(k): UnisportLocation(**v) for k, v in locations.items()},
            "live_validations": {int(k): int(v) for k, v in live_validations.items()},
        }

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        *,
        plain_response: bool = False,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return (
                    await response.json()
                    if not plain_response
                    else await response.text()
                )

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise UnisportApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise UnisportApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise UnisportApiClientError(
                msg,
            ) from exception
