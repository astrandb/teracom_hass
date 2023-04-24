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

from .const import DOMAIN, SIGNAL_UPDATE_TERACOM, TCW122B_CM, TCW181B_CM, TCW241, TCW242
from .pyteracom import TeracomAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch"]
SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup(
    hass: HomeAssistant, config: dict
):  # pylint: disable=unused-argument
    """Set up the Teracom TCW component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Teracom TCW from a config entry."""

    async def poll_update(event_time):  # pylint: disable=unused-argument
        #  _LOGGER.debug("Entered pollupdate")
        data = await _hassdata["api"].get_data()
        # _LOGGER.debug("Calling dispatcher_send")
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
        if model == TCW181B_CM:
            _hassdata["digital"] = root.find("DigitalInput").text == "CLOSED"
            for nox in range(1, 9):
                _hassdata[f"relay{nox}"] = root.find(f"Relay{nox}").text == "ON"
        if model in (TCW241,):
            for i in range(1, 5):
                _hassdata[f"analog{i}"] = _hassdata["data_dict"]["Monitor"]["AI"][
                    f"AI{i}"
                ]["value"]
            for i in range(1, 5):
                _hassdata[f"digital{i}"] = (
                    _hassdata["data_dict"]["Monitor"]["DI"][f"DI{i}"]["valuebin"] == "0"
                )
            for i in range(1, 9):
                value = _hassdata["data_dict"]["Monitor"]["S"][f"S{i}"]["item1"][
                    "value"
                ]
                _hassdata[f"sensor{i}"] = value if value != "---" else None
                value = _hassdata["data_dict"]["Monitor"]["S"][f"S{i}"]["item2"][
                    "value"
                ]
                _hassdata[f"sensor{i}b"] = value if value != "---" else None
        if model in (TCW241, TCW242):
            for i in range(1, 5):
                _hassdata[f"relay{i}"] = (
                    _hassdata["data_dict"]["Monitor"]["R"][f"R{i}"]["valuebin"] == "1"
                )

    hass.data[DOMAIN][entry.entry_id] = {}
    _hassdata = hass.data[DOMAIN][entry.entry_id]

    config = entry.data

    websession = async_get_clientsession(hass)
    _hassdata["api"] = TeracomAPI(
        websession=websession,
        host=config.get(CONF_HOST),
        username=config.get(CONF_USERNAME),
        password=config.get(CONF_PASSWORD),
    )
    result_text = await _hassdata["api"].get_data()

    try:
        result_dict = xmltodict.parse(result_text)
    except Exception as exc:  # pylint: disable=broad-except
        raise HomeAssistantError("Cannot parse response") from exc

    _hassdata["data_dict"] = result_dict
    _hassdata["xml"] = result_text

    if config.get("model") in (TCW122B_CM, TCW181B_CM):
        _hassdata["id"] = _hassdata["data_dict"]["Monitor"]["ID"].replace(":", "")
        _hassdata["device"] = _hassdata["data_dict"]["Monitor"]["Device"].strip()
        _hassdata["hostname"] = _hassdata["data_dict"]["Monitor"]["Hostname"].strip()
        _hassdata["fw"] = _hassdata["data_dict"]["Monitor"]["FW"].strip()
    else:
        _hassdata["id"] = _hassdata["data_dict"]["Monitor"]["DeviceInfo"]["ID"].replace(
            ":", ""
        )
        _hassdata["device"] = _hassdata["data_dict"]["Monitor"]["DeviceInfo"][
            "DeviceName"
        ].strip()
        _hassdata["hostname"] = _hassdata["data_dict"]["Monitor"]["DeviceInfo"][
            "HostName"
        ].strip()
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
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(**device_info)

    data = await _hassdata["api"].get_data()
    parse_response(data)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async_track_time_interval(hass, poll_update, SCAN_INTERVAL)
    dispatcher_send(hass, SIGNAL_UPDATE_TERACOM)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
