"""Entity class and helpers for Teracom integration."""
import logging

from homeassistant.core import callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

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
        state_class,
        unit_of_measurement,
    ):
        """Initialize the sensor."""
        self._data = hass.data[DOMAIN][entry.entry_id]
        self._attr_unique_id = self._data["id"] + "_" + name_short
        self._data_key = data_key
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._remove_dispatcher = None
        self._attr_name = name_long
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self._data["id"])},
        )
        self._attr_should_poll = False

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

    async def async_update(self):
        """Update the state."""
        #  _LOGGER.debug(self.name + " async_update 1 %s", self._api.heater_temperature)
        return
