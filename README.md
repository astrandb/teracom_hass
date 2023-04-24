[![teracom_hass](https://img.shields.io/github/v/release/astrandb/teracom_hass?include_prereleases)](https://github.com/astrandb/teracom_hass) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration) ![Validate with hassfest](https://github.com/astrandb/teracom_hass/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2023.svg) [![teracom_hass_downloads](https://img.shields.io/github/downloads/astrandb/teracom_hass/total)](https://github.com/astrandb/teracom_hass) [![teracom_hass_downloads](https://img.shields.io/github/downloads/astrandb/teracom_hass/latest/total)](https://github.com/astrandb/teracom_hass)

# Teracom TCW component for Home Assistant

Custom component to support Teracom TCW monitoring devices.

Supported models: TCW122B-CM, TCW181B-CM, TCW241, TCW242

## Installation

There are 2 different methods for installing the custom component

### HACS installation

_While this component can be installed by HACS, it is not included in the default repository of HACS._

1. Add this repository as a custom repository inside HACS settings. Make sure you select `Integration` as Category.
2. Install the component from the Integrations Overview page.
3. Back out and restart Home Assistant

### Git installation

1. Make sure you have git installed on your machine.
2. Navigate to you home assistant configuration folder.
3. Create a `custom_components` folder of it does not exist, navigate down into it after creation.
4. Execute the following command: `git clone https://github.com/astrandb/teracom_hass.git`

## Setup

Add the integration in  Settings->Integrations. Enter address and login credentials if needed. All available entites will be created.

## Development

It is recommended to use the included development container. PRs are welcome.
