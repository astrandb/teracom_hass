"""Config flow for Teracom TCW integration."""
import logging
import xml.etree.ElementTree as ET

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.components.rest.data import RestData
import pysnmp.hlapi.asyncio as hlapi
from pysnmp.hlapi.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    UsmUserData,
    getCmd,
)


from .const import DOMAIN, SNMP_ONLY_MODELS, SUPPORTED_MODELS  # pylint:disable=unused-import

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
        self._product_name = ""
        self._mac = ""
        self._hostname = ""

    async def authenticate(self, hass, username, password) -> bool:
        """Test if we can authenticate with the host."""
        request_args = [
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget((self.host, 161)),
            ContextData(),
        ]
        OID_PRODUCT_NAME = '1.3.6.1.4.1.38783.1.1.0'
        OID_MAC = '1.3.6.1.4.1.38783.2.1.4.0'
        OID_HOST_NAME = '1.3.6.1.4.1.38783.2.1.7.0'

        errindication, errorStatus, errorIndex, res_table = await getCmd(
            *request_args, ObjectType(ObjectIdentity(OID_PRODUCT_NAME))
        )
        if errindication:  # SNMP engine errors
            _LOGGER.error("ErrIndication: %s", errindication)
            return False
        if errorStatus:  # SNMP agent errors
            _LOGGER.error("errorStatus: %s at %s", errorStatus.prettyPrint(), res_table[int(errorIndex)-1] if errorIndex else '?')
            return False

        for res in res_table:
            _LOGGER.debug("Result: %s", res[1])
            self._product_name = res[1].asOctets().decode("utf-8")

        if self._product_name in SNMP_ONLY_MODELS:
            errindication, errorStatus, errorIndex, res_table = await getCmd(
                *request_args, ObjectType(ObjectIdentity(OID_HOST_NAME))
            )
            if errindication:  # SNMP engine errors
                _LOGGER.error("ErrIndication: %s", errindication)
                return False
            if errorStatus:  # SNMP agent errors
                _LOGGER.error("errorStatus: %s at %s", errorStatus.prettyPrint(), res_table[int(errorIndex)-1] if errorIndex else '?')
                return False

            for res in res_table:
                _LOGGER.debug("Hostname: %s", res[1])
                self._hostname = res[1].asOctets().decode("utf-8").strip()

            errindication, errorStatus, errorIndex, res_table = await getCmd(
                *request_args, ObjectType(ObjectIdentity(OID_MAC))
            )
            if errindication:  # SNMP engine errors
                _LOGGER.error("ErrIndication: %s", errindication)
                return False
            if errorStatus:  # SNMP agent errors
                _LOGGER.error("errorStatus: %s at %s", errorStatus.prettyPrint(), res_table[int(errorIndex)-1] if errorIndex else '?')
                return False

            for res in res_table:
                self._mac = res[1].asOctets().hex().upper()
                _LOGGER.debug("MAC: %s", self._mac)

            return True

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

    model = hub._product_name
    _LOGGER.debug("Model: [%s]", model)
    if model in SNMP_ONLY_MODELS:
        _LOGGER.debug("Model not fully supported yet: %s", model)
        title = hub._hostname + " - " + hub._mac
        return {"title": title, "id": hub._mac, "hostname": hub._hostname, "model": hub._product_name}

    # Return info that you want to store in the config entry.
    root = ET.fromstring(hub._xmldata)
    if root.tag == "Monitor":
        _LOGGER.debug("ID: %s", root.find("ID").text)

    model = root.find("Device").text.strip()
    _LOGGER.debug("Device: %s", model)
    if model not in SUPPORTED_MODELS:
        _LOGGER.debug("Model not supported: %s", model)
        raise ModelNotSupported(model)

    mac = root.find("ID").text.replace(":", "")
    hostname = root.find("Hostname").text.strip().title()
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
            user_input["model"] = info["model"]
            return self.async_create_entry(title=info["title"], data=user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except ModelNotSupported as mns:
            _LOGGER.warning("Model %s not supported", mns.args[0])
            errors["host"] = "model_not_supported"
            placeholders["model"] = mns.args[0]  # Does not work
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders=placeholders,  # Does not work
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class ModelNotSupported(exceptions.HomeAssistantError):
    """Error to indicate model not supported."""
