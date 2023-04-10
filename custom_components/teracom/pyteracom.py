"""pyteracom - library for teracom integration for Home Assistant."""

# Move to pypi.org when stable

from __future__ import annotations

import logging

from aiohttp import ClientResponse, ClientResponseError, ClientSession

_LOGGER = logging.getLogger(__name__)


class TeracomAPI:
    """Class to get data from Teracom devices."""

    def __init__(self, websession: ClientSession, host: str) -> None:
        """Initialize."""
        self._websession = websession
        self._host = host

    async def request(self, method, endpoint="", **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
            kwargs.pop("headers")

        print(f"http://{self._host}/{endpoint}")
        try:
            res = await self._websession.request(
                method,
                f"http://{self._host}/{endpoint}",
                allow_redirects=True,
                max_redirects=20,
                **kwargs,
                headers=headers,
            )
        except:
            _LOGGER.debug("History: %s", res.history)
            print(f"Exc: {res}")
        print(await res.text())
        res.raise_for_status()
        return res

    async def get_xml(self):
        """Get xml data."""
        res = await self._websession.get(
            "http://192.168.0.37/index.htm",
        )
        _LOGGER.debug("Response: %s", res)
        print(res.status)
        print(await res.text())
        return await res.text()

    async def get_data(self):
        """Get data from api."""
        try:
            res = await self.request("GET")
            return await res.json()
        except ClientResponseError as exc:
            _LOGGER.error(
                "API get_data failed. Status: %s, - %s", exc.code, exc.message
            )
