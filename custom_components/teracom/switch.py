"""Switches."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import TCW
from .entity import TcwEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the entry."""

    def get_entities():
        entities = []
        if config_entry.data["model"] in (TCW.TCW220, TCW.TCW122B_CM):
            nrx = range(1, 3)
        elif config_entry.data["model"] == TCW.TCW181B_CM:
            nrx = range(1, 9)
        elif config_entry.data["model"] in (TCW.TCW241, TCW.TCW242):
            nrx = range(1, 5)
        else:
            return entities
        if config_entry.data["model"] in (TCW.TCW122B_CM, TCW.TCW181B_CM):
            entities.extend(
                [
                    TcwSwitch(
                        hass,
                        config_entry,
                        f"relay{nox}",
                        None,
                        None,
                        None,
                    )
                    for nox in nrx
                ]
            )
        if config_entry.data["model"] in (TCW.TCW220, TCW.TCW241, TCW.TCW242):
            entities.extend(
                [
                    TcwSwitchGen2(
                        hass,
                        config_entry,
                        f"relay{nox}",
                        None,
                        None,
                        None,
                    )
                    for nox in nrx
                ]
            )
        return entities

    async_add_entities(get_entities())


class TcwSwitch(TcwEntity, SwitchEntity):
    """Representation of a switch."""

    @property
    def is_on(self):
        """Return state of switch."""
        return self._data.get(self._data_key)

    async def async_turn_on(self, **kwargs):
        """Turn switch on."""
        _LOGGER.debug(" Turn_on %s", self.name)
        await self._data["api"].set_relay(self._data_key[-1], 1)
        self._data[self._data_key] = True
        self.async_write_ha_state()
        # dispatcher_send(self.hass, SIGNAL_UPDATE_TERACOM)

    async def async_turn_off(self, **kwargs):
        """Turn switch off."""
        _LOGGER.debug(" Turn_off %s", self.name)
        await self._data["api"].set_relay(self._data_key[-1], 0)
        self._data[self._data_key] = False
        self.async_write_ha_state()
        # dispatcher_send(self.hass, SIGNAL_UPDATE_TERACOM)


class TcwSwitchGen2(TcwEntity, SwitchEntity):
    """Representation of a switch."""

    @property
    def is_on(self):
        """Return state of switch."""
        return self._data.get(self._data_key)

    async def async_turn_on(self, **kwargs):
        """Turn switch on."""
        _LOGGER.debug(" Turn_on %s", self.name)
        await self._data["api"].set_relay_g2(relay_no=self._data_key[-1], to_value="on")
        self._data[self._data_key] = True
        self.async_write_ha_state()
        # dispatcher_send(self.hass, SIGNAL_UPDATE_TERACOM)

    async def async_turn_off(self, **kwargs):
        """Turn switch off."""
        _LOGGER.debug(" Turn_off %s", self.name)
        await self._data["api"].set_relay_g2(
            relay_no=self._data_key[-1], to_value="off"
        )
        self._data[self._data_key] = False
        self.async_write_ha_state()
        # dispatcher_send(self.hass, SIGNAL_UPDATE_TERACOM)
