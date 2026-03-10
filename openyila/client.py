"""BLE client for communicating with YiLa door opener devices."""

import asyncio
import logging

from bleak import BleakClient
from bleak.exc import BleakError

from openyila.device import YilaDevice
from openyila.i18n import t
from openyila.protocol import (
    NUS_RX_CHAR_UUID,
    NUS_SERVICE_UUID,
    NUS_TX_CHAR_UUID,
    DeviceResponse,
    YilaProtocol,
)

logger = logging.getLogger(__name__)

# Timeouts matching the Android app
CONNECT_TIMEOUT = 10.0
RESPONSE_TIMEOUT = 6.0
DISCONNECT_DELAY = 0.5


class YilaClient:
    """BLE client for a single YiLa device.

    Handles connection, command sending, and response parsing over
    the Nordic UART Service.
    """

    def __init__(self, device: YilaDevice):
        self.device = device
        self._client: BleakClient | None = None
        self._response_event = asyncio.Event()
        self._response_data: bytes = b""

    def _notification_handler(self, _sender, data: bytearray):
        """Handle incoming BLE notifications (device responses)."""
        self._response_data = bytes(data)
        self._response_event.set()
        logger.debug(
            t("client.recv"),
            self._response_data,
            YilaProtocol.bytes_to_hex(self._response_data),
        )

    async def connect(self) -> None:
        """Connect to the device and set up Nordic UART Service notifications."""
        logger.info(t("client.connecting"), self.device.name, self.device.address)
        self._client = BleakClient(
            self.device.address, timeout=CONNECT_TIMEOUT
        )
        await self._client.connect()

        # Verify NUS service exists
        services = self._client.services
        nus = services.get_service(NUS_SERVICE_UUID)
        if nus is None:
            await self._client.disconnect()
            raise BleakError(
                t("client.no_nus", address=self.device.address)
            )

        # Subscribe to RX notifications
        await self._client.start_notify(NUS_RX_CHAR_UUID, self._notification_handler)
        logger.info(t("client.connected"), self.device.address)

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client and self._client.is_connected:
            try:
                await self._client.stop_notify(NUS_RX_CHAR_UUID)
            except Exception:
                pass
            await self._client.disconnect()
            logger.info(t("client.disconnected"), self.device.address)
        self._client = None

    async def _write_command(self, data: bytes) -> DeviceResponse:
        """Write a command and wait for the device response."""
        if not self._client or not self._client.is_connected:
            raise RuntimeError(t("client.not_connected"))

        self._response_event.clear()
        self._response_data = b""

        logger.debug(t("client.sending"), YilaProtocol.bytes_to_hex(data))

        # Write with response=False (WRITE_TYPE_NO_RESPONSE = 1)
        await self._client.write_gatt_char(NUS_TX_CHAR_UUID, data, response=False)

        try:
            await asyncio.wait_for(
                self._response_event.wait(), timeout=RESPONSE_TIMEOUT
            )
        except asyncio.TimeoutError:
            return DeviceResponse(success=False, message=t("client.timeout"))

        return YilaProtocol.parse_response(self._response_data)

    async def open(self) -> DeviceResponse:
        """Send the OPEN (unlock) command to the device.

        This triggers the door opener with the configured timing:
          - open_time: duration of the open signal (ms)
          - wait_time: pause between open and close (ms)
          - close_time: duration of the close signal (ms)
          - attribute: 0=normal (+), 1=reverse (-)
        """
        cmd = YilaProtocol.build_open_command(self.device)
        logger.info(
            t("client.unlocking"),
            self.device.address,
            t("client.mode_reverse") if self.device.is_reverse else t("client.mode_normal"),
            self.device.open_time,
            self.device.wait_time,
            self.device.close_time,
        )
        return await self._write_command(cmd)

    async def change_password(
        self, old_password: str, new_password: str
    ) -> DeviceResponse:
        """Send a password change command to the device.

        The new password must be a 6-digit numeric string.
        """
        if len(new_password) != 6 or not new_password.isdigit():
            raise ValueError(t("client.password_invalid"))

        cmd = YilaProtocol.build_change_password_command(old_password, new_password)
        logger.info(t("client.changing_pwd"), self.device.address)
        return await self._write_command(cmd)

    async def open_and_disconnect(self) -> DeviceResponse:
        """Connect, send open command, and disconnect."""
        try:
            await self.connect()
            response = await self.open()
            # Brief delay before disconnect (matches app behavior)
            await asyncio.sleep(DISCONNECT_DELAY)
            return response
        finally:
            await self.disconnect()


async def open_device(device: YilaDevice) -> DeviceResponse:
    """Convenience function: connect to a device, open it, and disconnect."""
    client = YilaClient(device)
    return await client.open_and_disconnect()

