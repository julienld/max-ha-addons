# Changelog

## 0.1.1

- Fix: Install `python3` and `pip3` in Dockerfile to fix build error.
- Fix: Ensure `client.py` is included in the build.
- Updated to remove `image` configuration to force local build.

## 0.1.0

- Initial release of the Lufa Farms Home Assistant Add-on.
- Features:
  - Automatic Order ID detection.
  - Sensors for Order Status, ETA, Stops Before, and Order Amount.
  - Native Home Assistant Supervisor API integration.
