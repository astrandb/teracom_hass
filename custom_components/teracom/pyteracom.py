"""pyteracom - Library for Teracom integration for Home Assistant."""

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

        try:
            res = await self._websession.request(
                method,
                f"http://{self._host}/{endpoint}",
                allow_redirects=True,
                max_redirects=20,
                **kwargs,
                headers=headers,
            )
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("History: %s", res.history)
        res.raise_for_status()
        return res

    async def get_data(self, username=None, password=None):
        """Get data from api."""
        try:
            auth = "" if username is None else f"?a={username}:{password}"
            response = await self.request("GET", f"status.xml{auth}")
        except ClientResponseError as exc:
            _LOGGER.error(
                "API get_data failed. Status: %s, - %s", exc.code, exc.message
            )
        return await response.text()

    async def set_relay(self, relay_no, to_state, username=None, password=None):
        """Set the relay state."""
        try:
            auth = "" if username is None else f"?a={username}:{password}&"
            auth = "?a=admin:admin&"
            response = await self.request(
                "GET", f"status.xml{auth}r{relay_no}={to_state}"
            )
        except ClientResponseError as exc:
            _LOGGER.error(
                "API set_relay failed. Status: %s, - %s", exc.code, exc.message
            )
        return await response.text()

    async def set_relay_g2(
        self, username=None, password=None, relay_no=3, to_value="off"
    ):
        """Set relay state."""
        print(f"relay_no={relay_no}")
        try:
            auth = "" if username is None else f"?a={username}:{password}&"
            auth = "?a=admin:admin&"
            cmd = "ron=" if to_value == "on" else "rof="
            rel_no = 2 ** (int(relay_no) - 1)
            print(f"status.xml{auth}{cmd}{rel_no}")
            response = await self.request("GET", f"status.xml{auth}{cmd}{rel_no}")
        except ClientResponseError as exc:
            _LOGGER.error(
                "API set_relay failed. Status: %s, - %s", exc.code, exc.message
            )
        return await response.text()
