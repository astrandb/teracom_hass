"""Constants for the Teracom TCW integration."""

from enum import StrEnum

DOMAIN = "teracom"
SIGNAL_UPDATE_TERACOM = "signal_update_teracom"
VERSION = "2024.12.0"


class TCW(StrEnum):
    """Supported TCW models."""

    TCW122B_CM = "TCW122B-CM"
    TCW181B_CM = "TCW181B-CM"
    TCW220 = "TCW220"
    TCW241 = "TCW241"
    TCW242 = "TCW242"
