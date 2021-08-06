"""Switches"""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.dispatcher import dispatcher_send

from .const import SIGNAL_UPDATE_TERACOM
from .entity import TcwEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    def get_entities():
        sensors = []
        if config_entry.data["model"] == "TCW122B-CM":
            nr = range(1, 3)
        elif config_entry.data["model"] == "TCW181B-CM":
            nr = range(1, 9)
        for no in nr:
            sensors.append(
                TcwSwitch(
                    hass,
                    config_entry,
                    "relay" + str(no),
                    "relay" + str(no),
                    "Relay " + str(no),
                    None,
                    None,
                    None,
                )
            )
        return sensors

    async_add_entities(await hass.async_add_job(get_entities), True)


class TcwSwitch(TcwEntity, SwitchEntity):
    """Representation of a switch."""

    @property
    def is_on(self):
        return self._data.get(self._data_key)

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_on")
        await self._data["api"].set_relay(self._data_key[-1], 1)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_TERACOM)

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_off")
        await self._data["api"].set_relay(self._data_key[-1], 0)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_TERACOM)
