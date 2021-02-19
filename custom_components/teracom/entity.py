"""Entity class and helpers for Teracom integration."""
import logging

from homeassistant.core import callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SIGNAL_UPDATE_TERACOM

_LOGGER = logging.getLogger(__name__)


class TcwEntity(Entity):
    """Representation of a sensor."""

    def __init__(
        self,
        hass,
        entry,
        data_key,
        name_short,
        name_long,
        device_class,
        unit_of_measurement,
    ):
        """Initialize the sensor."""
        self._entry_id = entry.entry_id
        self._unique_id = hass.data[DOMAIN][entry.entry_id]["id"] + "_" + name_short
        self._data = hass.data[DOMAIN][entry.entry_id]
        self._data_key = data_key
        self._name_long = (
            "tcw_" + hass.data[DOMAIN][entry.entry_id]["id"] + "_" + name_long
        )
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._remove_dispatcher = async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_TERACOM, self._update_callback
        )

    @callback
    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)

    async def async_will_remove_from_hass(self):
        self._remove_dispatcher()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name_long

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def device_info(self):
        return {
            "connections": {(CONNECTION_NETWORK_MAC, self._data["id"])},
        }

    @property
    def should_poll(self):
        return False

    @property
    def device_class(self):
        return self._device_class

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        #  _LOGGER.debug(self.name + " async_update 1 %s", self._api.heater_temperature)
        return
