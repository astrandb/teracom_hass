[![teracom_hass](https://img.shields.io/github/v/release/astrandb/teracom_hass?include_prereleases)](https://github.com/astrandb/teracom_hass) [![hacs_badge](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/integration) ![Validate with hassfest](https://github.com/astrandb/teracom_hass/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2025.svg) [![teracom_hass_downloads](https://img.shields.io/github/downloads/astrandb/teracom_hass/total)](https://github.com/astrandb/teracom_hass) [![teracom_hass_downloads](https://img.shields.io/github/downloads/astrandb/teracom_hass/latest/total)](https://github.com/astrandb/teracom_hass)

# Teracom TCW component for Home Assistant

Custom component to support Teracom TCW monitoring devices.

Supported models: TCW122B-CM, TCW181B-CM, TCW220, TCW241, TCW242

## Installation

### Preferred download and setup method

- Use HACS
- Search for the integration Teracom and download the integration.
- Restart Home Assistant
- Go to Settings->Devices & Services->Integrations and press Add Integration. Search for Teracom and select it. Follow the prompts.

### Manual download and setup method

- Copy all files from custom_components/teracom_hass in this repo to your config custom_components/teracom_hass
- Restart Home Assistant
- Go to Settings->Devices & Services->Integrations and press Add Integration. Search for Teracom and select it. Follow the prompts.

## Setup

Add the integration in  Settings->Integrations. Enter address and login credentials if needed. All available entites will be created.

## Development

It is recommended to use the included development container. PRs are welcome.
