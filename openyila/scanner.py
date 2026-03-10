"""BLE scanner for YiLa devices."""

import asyncio
import logging

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from openyila.i18n import t
from openyila.protocol import YilaProtocol

logger = logging.getLogger(__name__)

# Scan timeout matching the app's 6-second default
DEFAULT_SCAN_TIMEOUT = 6.0


class YilaScanner:
    """Scans for YiLa BLE devices.

    YiLa devices are identified by having "YILA" in their advertised name.
    """

    def __init__(self, scan_timeout: float = DEFAULT_SCAN_TIMEOUT):
        self.scan_timeout = scan_timeout

    async def scan(self) -> list[dict]:
        """Scan for YiLa devices and return a list of discovered devices.

        Returns a list of dicts with keys: address, name, rssi, battery_level.
        """
        found: dict[str, dict] = {}

        def _callback(device: BLEDevice, adv: AdvertisementData):
            name = adv.local_name or device.name or ""
            if "YILA" not in name.upper():
                return

            battery = None
            if adv.manufacturer_data:
                for _company_id, mfr_bytes in adv.manufacturer_data.items():
                    battery = YilaProtocol.parse_battery_from_adv(mfr_bytes)
                    if battery is not None:
                        break

            found[device.address] = {
                "address": device.address,
                "name": name,
                "rssi": adv.rssi,
                "battery_level": battery,
            }
            logger.info(
                t("scanner.found"),
                name,
                device.address,
                adv.rssi or 0,
                battery,
            )

        scanner = BleakScanner(detection_callback=_callback)
        await scanner.start()
        await asyncio.sleep(self.scan_timeout)
        await scanner.stop()

        return list(found.values())
