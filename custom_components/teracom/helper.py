"""Helpers for Teracom integration"""
import logging
import xml.etree.ElementTree as ET

from homeassistant.components.rest.data import RestData

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class TcwApi:
    def __init__(self, hass, entry, host, user, password):
        self._hass = hass
        self._hassdata = hass.data[DOMAIN][entry.entry_id]
        self._host = host
        self._user = user
        self._password = password
        return

    def parse_response(self, data):
        self._hassdata["xml"] = data
        root = ET.fromstring(data)
        model = root.find("Device").text.strip()
        if model == "TCW122B-CM":
            self._hassdata["temperature1"] = (
                None
                if root.find("Temperature1").text == "---"
                else float(root.find("Temperature1").text[0:-2])
            )
            self._hassdata["temperature2"] = (
                None
                if root.find("Temperature2").text == "---"
                else float(root.find("Temperature2").text[0:-2])
            )
            self._hassdata["humidity1"] = (
                None
                if root.find("Humidity1").text == "---"
                else float(root.find("Humidity1").text[0:-1])
            )
            self._hassdata["humidity2"] = (
                None
                if root.find("Humidity2").text == "---"
                else float(root.find("Humidity2").text[0:-1])
            )
            self._hassdata["voltage1"] = float(root.find("AnalogInput1").text[0:-1])
            self._hassdata["voltage2"] = float(root.find("AnalogInput2").text[0:-1])
            self._hassdata["digital1"] = root.find("DigitalInput1").text == "CLOSED"
            self._hassdata["digital2"] = root.find("DigitalInput2").text == "CLOSED"
            self._hassdata["relay1"] = root.find("Relay1").text == "ON"
            self._hassdata["relay2"] = root.find("Relay2").text == "ON"
        elif model == "TCW181B-CM":
            self._hassdata["digital"] = root.find("DigitalInput").text == "CLOSED"
            for no in range(1, 9):
                self._hassdata["relay" + str(no)] = root.find("Relay" + str(no)).text == "ON"

    async def set_relay(self, relay_no, to_state):
        method = "GET"
        payload = auth = None
        verify_ssl = False
        headers = {}
        _ENDPOINT = f"http://{self._host}/status.xml?r{relay_no}={to_state}"

        rest = RestData(
            self._hass, method, _ENDPOINT, auth, headers, None, payload, verify_ssl
        )
        await rest.async_update()

        if rest.data is None:
            _LOGGER.error("Unable to fetch data from device - set_relay()")
            return
        self.parse_response(rest.data)
        return

    async def get_data(self):
        method = "GET"
        payload = auth = None
        verify_ssl = False
        headers = {}
        _ENDPOINT = f"http://{self._host}/status.xml"

        rest = RestData(
            self._hass, method, _ENDPOINT, auth, headers, None, payload, verify_ssl
        )
        await rest.async_update()

        if rest.data is None:
            _LOGGER.error("Unable to fetch data from device - get_data()")
            return
        self.parse_response(rest.data)
        return
