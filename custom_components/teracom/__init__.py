"""The Teracom TCW integration."""
import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import timedelta

from homeassistant.components.rest.data import RestData
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, SIGNAL_UPDATE_TERACOM
from .helper import TcwApi

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
        await _hassdata["api"].get_data()
        #  _LOGGER.debug("Calling dispatcher_send")
        dispatcher_send(hass, SIGNAL_UPDATE_TERACOM)

    hass.data[DOMAIN][entry.entry_id] = {}
    _hassdata = hass.data[DOMAIN][entry.entry_id]

    config = entry.data
    _hassdata["api"] = TcwApi(
        hass, entry, config.get("host"), config.get("user"), config.get("password")
    )
    method = "GET"
    payload = None
    auth = None
    # verify_ssl = DEFAULT_VERIFY_SSL
    headers = {}
    endpoint = f"http://{config.get('host')}/status.xml"

    try:
        rest = RestData(hass, method, endpoint, "", auth, headers, None, payload, False)
        await rest.async_update()
    except Exception as err:
        raise ConfigEntryNotReady from err

    if rest.data is None:
        _LOGGER.error("Unable to fetch data from device - async-setup_entry()")
        return False

    # Process rest.data to find static values as device_name etc
    _hassdata["xml"] = rest.data
    root = ET.fromstring(rest.data)
    _hassdata["id"] = root.find("ID").text.replace(":", "")
    _hassdata["device"] = root.find("Device").text.strip()
    _hassdata["hostname"] = root.find("Hostname").text.strip().title()
    _hassdata["fw"] = root.find("FW").text
    _LOGGER.debug("setup_entry: %s", entry.entry_id)

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

    await _hassdata["api"].get_data()

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
