[![teracom_hass](https://img.shields.io/github/v/release/astrandb/teracom_hass?include_prereleases)](https://github.com/astrandb/teracom_hass) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Validate with hassfest](https://github.com/astrandb/teracom_hass/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2021.svg) [![senz_hass_downloads](https://img.shields.io/github/downloads/astrandb/teracom_hass/total)](https://github.com/astrandb/teracom_hass)

# Teracom TCW component for Home Assistant

Custom component to support Teracom TCW monitoring devices.

## Installation

There are 2 different methods of installing the custom component

### HACS installation

_While this component can be installed by HACS, it is not included in the default repository of HACS._

1. Add this repository as a custom repository inside HACS settings. Make sure you select `Integration` as Category.
2. Install the component from the Integrations Overview page.

### Git installation

1. Make sure you have git installed on your machine.
2. Navigate to you home assistant configuration folder.
3. Create a `custom_components` folder of it does not exist, navigate down into it after creation.
4. Execute the following command: `git clone https://github.com/astrandb/teracom_hass.git`

## Configuration

Configuration is done through in Configuration > Integrations where you first configure it and then set the options for what you want to monitor.

## Development

This project uses `black` and `isort` for code formatting and `flake8` for linting.
Always run

```
make lint
```

Before pushing your changes
