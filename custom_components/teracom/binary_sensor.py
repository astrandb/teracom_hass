"""Binary sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import TCW122B_CM, TCW181B_CM, TCW241
from .entity import TcwEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the binary sensors."""

    def get_entities():
        sensors = []
        if config_entry.data["model"] == TCW122B_CM:
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital1",
                    None,
                    None,
                    None,
                )
            )
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital2",
                    None,
                    None,
                    None,
                )
            )
        elif config_entry.data["model"] == TCW181B_CM:
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital",
                    None,
                    None,
                    None,
                )
            )
        elif config_entry.data["model"] in (TCW241,):
            sensors.extend(
                [
                    TcwBinarySensor(
                        hass,
                        config_entry,
                        f"digital{i}",
                        None,
                        None,
                        None,
                    )
                    for i in range(1, 5)
                ]
            )
        return sensors

    async_add_entities(get_entities())


class TcwBinarySensor(TcwEntity):
    """Representation of a sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._data.get(self._data_key)
