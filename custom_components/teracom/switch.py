"""Switches."""
import logging

from homeassistant.components.switch import SwitchEntity

from .const import TCW122B_CM, TCW181B_CM, TCW241, TCW242
from .entity import TcwEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the entry."""

    def get_entities():
        entities = []
        if config_entry.data["model"] == TCW122B_CM:
            nrx = range(1, 3)
        elif config_entry.data["model"] == TCW181B_CM:
            nrx = range(1, 9)
        elif config_entry.data["model"] in (TCW241, TCW242):
            nrx = range(1, 5)
        else:
            return entities
        if config_entry.data["model"] in (TCW122B_CM, TCW181B_CM):
            for nox in nrx:
                entities.append(
                    TcwSwitch(
                        hass,
                        config_entry,
                        f"relay{nox}",
                        None,
                        None,
                        None,
                    )
                )
        if config_entry.data["model"] in (TCW241, TCW242):
            for nox in nrx:
                entities.append(
                    TcwSwitchGen2(
                        hass,
                        config_entry,
                        f"relay{nox}",
                        None,
                        None,
                        None,
                    )
                )
        return entities

    async_add_entities(await hass.async_add_job(get_entities), True)


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
