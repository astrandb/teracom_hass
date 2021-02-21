"""Sensors"""
#  import logging
from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    PERCENTAGE,
    TEMP_CELSIUS,
    VOLT,
)

from .entity import TcwEntity

#  _LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    def get_entities():
        sensors = []
        if config_entry.data["model"] == "TCW122B-CM":
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "temperature1",
                    "temp1",
                    "Temperature 1",
                    DEVICE_CLASS_TEMPERATURE,
                    TEMP_CELSIUS,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "temperature2",
                    "temp2",
                    "Temperature 2",
                    DEVICE_CLASS_TEMPERATURE,
                    TEMP_CELSIUS,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "humidity1",
                    "hum1",
                    "Humidity 1",
                    DEVICE_CLASS_HUMIDITY,
                    PERCENTAGE,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "humidity2",
                    "hum2",
                    "Humidity 2",
                    DEVICE_CLASS_HUMIDITY,
                    PERCENTAGE,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "voltage1",
                    "volt1",
                    "Voltage 1",
                    DEVICE_CLASS_VOLTAGE,
                    VOLT,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "voltage2",
                    "volt2",
                    "Voltage 2",
                    DEVICE_CLASS_VOLTAGE,
                    VOLT,
                )
            )
        return sensors

    async_add_entities(await hass.async_add_job(get_entities), True)


class TcwSensor(TcwEntity):
    """Representation of a sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._data.get(self._data_key)

    @property
    def entity_registry_enabled_default(self):
        """Disable sensor if not used."""
        #  _LOGGER.debug("Enable sensor: %s", self._data[self._data_key])
        return self._data[self._data_key] is not None
