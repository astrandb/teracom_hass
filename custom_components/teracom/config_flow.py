"""Config flow for Teracom TCW integration."""

import logging

import voluptuous as vol
import xmltodict

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN, TCW  # pylint:disable=unused-import
from .pyteracom import TeracomAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Optional(CONF_USERNAME): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Optional(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


class TcwHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host):
        """Initialize."""
        self.host = host
        self.xmldata = ""
        self.data_dict = {}

    async def authenticate(self, hass, username, password) -> bool:
        """Test if we can authenticate with the host."""

        websession = async_get_clientsession(hass)

        api = TeracomAPI(
            websession=websession, host=self.host, username=username, password=password
        )
        result_text = await api.get_data()

        try:
            result_dict = xmltodict.parse(result_text)
        except Exception as exc:  # pylint: disable=broad-except
            raise HomeAssistantError("Cannot parse response") from exc

        self.data_dict = result_dict
        self.xmldata = result_text
        return True


async def validate_input(hass: HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    hub = TcwHub(data["host"])

    if not await hub.authenticate(hass, data.get("username"), data.get("password")):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    # root = ET.fromstring(hub.xmldata)
    # if root.tag == "Monitor":
    #     _LOGGER.debug("ID: %s", root.find("ID").text)

    model = hub.data_dict["Monitor"].get("Device")
    if model is None:
        model = hub.data_dict["Monitor"]["DeviceInfo"].get("DeviceName")
    _LOGGER.debug("Device: %s", model)

    if model not in TCW:
        _LOGGER.debug("Model not supported: %s", model)
        raise ModelNotSupported(model)

    if model in (TCW.TCW122B_CM, TCW.TCW181B_CM):
        mac = hub.data_dict["Monitor"].get("ID")
        hostname = hub.data_dict["Monitor"].get("Hostname")
    else:
        mac = hub.data_dict["Monitor"]["DeviceInfo"].get("ID")
        hostname = hub.data_dict["Monitor"]["DeviceInfo"].get("HostName")
    mac = mac.replace(":", "")
    hostname = hostname.strip()
    title = hostname + " - " + mac
    return {"title": title, "id": mac, "hostname": hostname, "model": model}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Teracom TCW."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}
        placeholders = {}

        try:
            info = await validate_input(self.hass, user_input)
            await self.async_set_unique_id(info["id"])
            self._abort_if_unique_id_configured()
            user_input["model"] = info["model"]
            return self.async_create_entry(title=info["title"], data=user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except ModelNotSupported as mns:
            _LOGGER.debug("Model %s not supported", mns.args[0])
            errors["host"] = "model_not_supported"
            placeholders = {"model": mns.args[0]}
        except AbortFlow:
            errors["base"] = "already_configured"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception: %s")
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders=placeholders,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class ModelNotSupported(HomeAssistantError):
    """Error to indicate model not supported."""
