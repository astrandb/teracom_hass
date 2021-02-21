"""Config flow for Teracom TCW integration."""
import logging
import xml.etree.ElementTree as ET

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.components.rest.data import RestData

from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {"host": str, vol.Optional("username"): str, vol.Optional("password"): str}
)


class TcwHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host):
        """Initialize."""
        self.host = host
        self._xmldata = ""

    async def authenticate(self, hass, username, password) -> bool:
        """Test if we can authenticate with the host."""

        method = "GET"
        payload = auth = None
        verify_ssl = False
        headers = {}
        _ENDPOINT = f"http://{self.host}/status.xml"

        rest = RestData(
            hass, method, _ENDPOINT, auth, headers, None, payload, verify_ssl
        )
        await rest.async_update()

        if rest.data is None:
            _LOGGER.error("Unable to fetch data from device")
            return False
        # TODO process rest.data to find device name etc
        self._xmldata = rest.data

        return True


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    hub = TcwHub(data["host"])

    if not await hub.authenticate(
        hass, data.get("username", None), data.get("password", None)
    ):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    root = ET.fromstring(hub._xmldata)
    if root.tag == "Monitor":
        _LOGGER.debug("ID: %s", root.find("ID").text)
    mac = root.find("ID").text.replace(":", "")
    hostname = root.find("Hostname").text.strip().title()
    title = hostname + " - " + mac
    return {"title": title, "id": mac, "hostname": hostname}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Teracom TCW."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
            await self.async_set_unique_id(info["id"])
            return self.async_create_entry(title=info["title"], data=user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
