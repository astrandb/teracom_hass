"""The Teracom TCW integration."""
import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import timedelta

import xmltodict
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, SIGNAL_UPDATE_TERACOM, TCW122B_CM, TCW181B_CM, TCW241
from .pyteracom import TeracomAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch"]
SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Teracom TCW component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Teracom TCW from a config entry."""

    async def poll_update(event_time):
        #  _LOGGER.debug("Entered pollupdate")
        data = await _hassdata["api"].get_data(
            config.get(CONF_USERNAME), config.get(CONF_PASSWORD)
        )
        _LOGGER.debug("Calling dispatcher_send")
        parse_response(data)
        dispatcher_send(hass, SIGNAL_UPDATE_TERACOM)

    def parse_response(data):
        """Parse the response."""
        _hassdata["xml"] = data
        try:
            result_dict = xmltodict.parse(data)
        except Exception as exc:  # pylint: disable=broad-except
            raise HomeAssistantError("Cannot parse response") from exc
        _hassdata["data_dict"] = result_dict
        root = ET.fromstring(data)
        model = config["model"]
        if model == TCW122B_CM:
            _hassdata["temperature1"] = (
                None
                if root.find("Temperature1").text == "---"
                else float(root.find("Temperature1").text[0:-2])
            )
            _hassdata["temperature2"] = (
                None
                if root.find("Temperature2").text == "---"
                else float(root.find("Temperature2").text[0:-2])
            )
            _hassdata["humidity1"] = (
                None
                if root.find("Humidity1").text == "---"
                else float(root.find("Humidity1").text[0:-1])
            )
            _hassdata["humidity2"] = (
                None
                if root.find("Humidity2").text == "---"
                else float(root.find("Humidity2").text[0:-1])
            )
            _hassdata["voltage1"] = float(root.find("AnalogInput1").text[0:-1])
            _hassdata["voltage2"] = float(root.find("AnalogInput2").text[0:-1])
            _hassdata["digital1"] = root.find("DigitalInput1").text == "CLOSED"
            _hassdata["digital2"] = root.find("DigitalInput2").text == "CLOSED"
            _hassdata["relay1"] = root.find("Relay1").text == "ON"
            _hassdata["relay2"] = root.find("Relay2").text == "ON"
        elif model == TCW181B_CM:
            _hassdata["digital"] = root.find("DigitalInput").text == "CLOSED"
            for nox in range(1, 9):
                _hassdata[f"relay{nox}"] = root.find(f"Relay{nox}").text == "ON"
        elif model == TCW241:
            _hassdata["digital1"] = (
                _hassdata["data_dict"]["Monitor"]["DI"]["DI1"]["valuebin"] == "0"
            )
            _hassdata["digital2"] = (
                _hassdata["data_dict"]["Monitor"]["DI"]["DI2"]["valuebin"] == "0"
            )
            _hassdata["digital3"] = (
                _hassdata["data_dict"]["Monitor"]["DI"]["DI3"]["valuebin"] == "0"
            )
            _hassdata["digital4"] = (
                _hassdata["data_dict"]["Monitor"]["DI"]["DI4"]["valuebin"] == "0"
            )
            _hassdata["relay1"] = (
                _hassdata["data_dict"]["Monitor"]["R"]["R1"]["valuebin"] == "1"
            )
            _hassdata["relay2"] = (
                _hassdata["data_dict"]["Monitor"]["R"]["R2"]["valuebin"] == "1"
            )
            _hassdata["relay3"] = (
                _hassdata["data_dict"]["Monitor"]["R"]["R3"]["valuebin"] == "1"
            )
            _hassdata["relay4"] = (
                _hassdata["data_dict"]["Monitor"]["R"]["R4"]["valuebin"] == "1"
            )

    hass.data[DOMAIN][entry.entry_id] = {}
    _hassdata = hass.data[DOMAIN][entry.entry_id]

    config = entry.data

    websession = async_get_clientsession(hass)
    _hassdata["api"] = TeracomAPI(websession=websession, host=config.get(CONF_HOST))
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    auth = "" if config.get("username") is None else f"?a={username}:{password}"
    result = await _hassdata["api"].request(method="GET", endpoint=f"status.xml{auth}")
    result.raise_for_status()

    try:
        result_dict = xmltodict.parse(await result.text())
    except Exception as exc:  # pylint: disable=broad-except
        raise HomeAssistantError("Cannot parse response") from exc

    _hassdata["data_dict"] = result_dict
    _hassdata["xml"] = await result.text()

    if config.get("model") in (TCW122B_CM, TCW181B_CM):
        _hassdata["id"] = _hassdata["data_dict"]["Monitor"]["ID"].replace(":", "")
        _hassdata["device"] = _hassdata["data_dict"]["Monitor"]["Device"].strip()
        _hassdata["hostname"] = (
            _hassdata["data_dict"]["Monitor"]["Hostname"].strip().title()
        )
        _hassdata["fw"] = _hassdata["data_dict"]["Monitor"]["FW"].strip()
    else:
        _hassdata["id"] = _hassdata["data_dict"]["Monitor"]["DeviceInfo"]["ID"].replace(
            ":", ""
        )
        _hassdata["device"] = _hassdata["data_dict"]["Monitor"]["DeviceInfo"][
            "DeviceName"
        ].strip()
        _hassdata["hostname"] = (
            _hassdata["data_dict"]["Monitor"]["DeviceInfo"]["HostName"].strip().title()
        )
        _hassdata["fw"] = _hassdata["data_dict"]["Monitor"]["DeviceInfo"][
            "FwVer"
        ].strip()

    device_info = DeviceInfo(
        connections={(dr.CONNECTION_NETWORK_MAC, _hassdata["id"])},
        manufacturer="Teracom",
        model=_hassdata["device"],
        name=_hassdata["hostname"],
        sw_version=_hassdata["fw"],
        config_entry_id=entry.entry_id,
        configuration_url=f"http://{config.get('host')}",
    )
    _LOGGER.debug("Adding or updating teracom device %s", _hassdata["id"])
    # device_registry = await hass.helpers.device_registry.async_get_registry()
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(**device_info)

    data = await _hassdata["api"].get_data(
        config.get(CONF_USERNAME), config.get(CONF_PASSWORD)
    )
    parse_response(data)

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    async_track_time_interval(hass, poll_update, SCAN_INTERVAL)
    dispatcher_send(hass, SIGNAL_UPDATE_TERACOM)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
