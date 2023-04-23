"""Binary sensors"""

from .const import TCW122B_CM, TCW181B_CM, TCW241
from .entity import TcwEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the binary sensors."""

    def get_entities():
        sensors = []
        if config_entry.data["model"] == TCW122B_CM:
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital1",
                    "dig1",
                    "Digital input 1",
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
                    "dig2",
                    "Digital input 2",
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
                    "dig",
                    "Digital input",
                    None,
                    None,
                    None,
                )
            )
        elif config_entry.data["model"] == TCW241:
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital1",
                    "dig1",
                    "Digital input 1",
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
                    "dig2",
                    "Digital input 2",
                    None,
                    None,
                    None,
                ),
            )
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital3",
                    "dig3",
                    "Digital input 3",
                    None,
                    None,
                    None,
                ),
            )
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital4",
                    "dig4",
                    "Digital input 4",
                    None,
                    None,
                    None,
                ),
            )
        return sensors

    async_add_entities(await hass.async_add_job(get_entities), True)


class TcwBinarySensor(TcwEntity):
    """Representation of a sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._data.get(self._data_key)
