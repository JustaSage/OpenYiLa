"""YiLa BLE command protocol.

Implements the encryption and command building logic reverse-engineered
from the YiLa door opener Android app (com.macronum.bledemo).

Protocol:
  1. Derive key: MD5(password)[8:24]  (16 hex chars)
  2. Build plaintext: "{unix_timestamp}{key}{payload}"
  3. Pad plaintext to 16-byte boundary (zero-pad)
  4. AES/ECB encrypt with fixed key "Fx4k6AWivOsLE4NI"
  5. Send encrypted bytes over BLE Nordic UART TX characteristic
"""

import hashlib
import re
import time
from dataclasses import dataclass

from Crypto.Cipher import AES

from openyila.device import YilaDevice
from openyila.i18n import t

# Fixed AES key used by the app for outer encryption
_AES_KEY = b"Fx4k6AWivOsLE4NI"

# Nordic UART Service UUIDs
NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # Write (phone→device)
NUS_RX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # Notify (device→phone)
CCCD_UUID = "00002902-0000-1000-8000-00805f9b34fb"


@dataclass
class DeviceResponse:
    """Parsed response from a YiLa device."""

    success: bool
    battery_level: int | None = None
    message: str = ""


class YilaProtocol:
    """Builds and parses YiLa BLE commands."""

    @staticmethod
    def md5_hex(text: str) -> str:
        """Return lowercase hex MD5 digest of the given text."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _derive_key(password: str) -> str:
        """Derive the 16-char hex key from a password: MD5(password)[8:24]."""
        return YilaProtocol.md5_hex(password)[8:24]

    @staticmethod
    def _build_plaintext(key: str, payload: str) -> str:
        """Build the plaintext string: '{timestamp}{key}{payload}'."""
        timestamp = int(time.time())
        return f"{timestamp}{key}{payload}"

    @staticmethod
    def _aes_encrypt(plaintext: str) -> bytes:
        """AES/ECB encrypt with the fixed key, padding to 16-byte boundary."""
        data = plaintext.encode("utf-8")
        remainder = len(data) % 16
        if remainder != 0:
            data += b"\x00" * (16 - remainder)
        cipher = AES.new(_AES_KEY, AES.MODE_ECB)
        return cipher.encrypt(data)

    @classmethod
    def build_open_command(cls, device: YilaDevice) -> bytes:
        """Build the OPEN (unlock) command for a device.

        Command payload: "A:OPEN;P:{+|-} {openTime},{waitTime},{closeTime};"
          - '+' for normal mode (attribute=0)
          - '-' for reverse mode (attribute=1)
        """
        if not device.password:
            raise ValueError("Device password is required")

        key = cls._derive_key(device.password)
        direction = "-" if device.is_reverse else "+"
        payload = (
            f"A:OPEN;P:{direction} "
            f"{device.open_time},{device.wait_time},{device.close_time};"
        )
        plaintext = cls._build_plaintext(key, payload)
        return cls._aes_encrypt(plaintext)

    @classmethod
    def build_change_password_command(
        cls, old_password: str, new_password: str
    ) -> bytes:
        """Build the password change command.

        Command payload: "A:PW;P:{MD5(new_password)[8:24]};"
        Encrypted using old_password's derived key.
        """
        if not old_password or not new_password:
            raise ValueError("Both old and new passwords are required")

        old_key = cls._derive_key(old_password)
        new_key = cls._derive_key(new_password)
        payload = f"A:PW;P:{new_key};"
        plaintext = cls._build_plaintext(old_key, payload)
        return cls._aes_encrypt(plaintext)

    @classmethod
    def build_init_password_command(
        cls, old_password: str, new_password: str
    ) -> bytes:
        """Build the initialize password command (same format as change)."""
        return cls.build_change_password_command(old_password, new_password)

    @staticmethod
    def parse_response(data: bytes) -> DeviceResponse:
        """Parse a response received from the device.

        The device can respond with:
          - ASCII "OK" → success
          - ASCII "ERROR" or "FAIL" → failure (password error)
          - Single byte 1-5 → battery level
          - "BAT{N}" or "BATTERY{N}" patterns → battery level
        """
        if not data:
            return DeviceResponse(success=False, message=t("proto.empty"))

        battery = None

        # Try single-byte battery
        if len(data) == 1:
            val = data[0] & 0xFF
            if 1 <= val <= 5:
                battery = val

        # Try ASCII interpretation
        text = ""
        for b in data:
            if b == 9 or b == 10 or b == 13 or (32 <= b <= 126):
                text += chr(b)

        upper = text.upper()

        # Check for battery pattern in text
        if battery is None:
            m = re.search(r"(?:BAT|BATT|BATTERY|PWR|POWER)\D*([1-5])", upper)
            if m:
                battery = int(m.group(1))

        if "OK" in upper:
            return DeviceResponse(success=True, battery_level=battery, message="OK")

        if "ERROR" in upper:
            return DeviceResponse(success=False, battery_level=battery, message=t("proto.pwd_error"))

        if "FAIL" in upper:
            return DeviceResponse(success=False, battery_level=battery, message="FAIL")

        # Check hex representation
        hex_str = data.hex().upper()
        if "4F4B" in hex_str:  # "OK" in hex
            return DeviceResponse(success=True, battery_level=battery, message="OK")
        if "4552524F52" in hex_str:  # "ERROR" in hex
            return DeviceResponse(
                success=False, battery_level=battery, message="ERROR"
            )

        return DeviceResponse(
            success=False, battery_level=battery, message=t("proto.unknown")
        )

    @staticmethod
    def parse_battery_from_adv(manufacturer_data: bytes) -> int | None:
        """Parse battery level (1-5) from BLE advertisement manufacturer data.

        Scans vendor data blocks; the last byte in range 1-5 is the battery level.
        """
        if not manufacturer_data:
            return None

        i = 0
        while i < len(manufacturer_data) - 2:
            length = manufacturer_data[i] & 0xFF
            if length == 0:
                break
            if i + 1 < len(manufacturer_data):
                data_start = i + 2
                data_end = data_start + (length - 1)
                if data_end <= len(manufacturer_data) and length > 1:
                    last_byte = manufacturer_data[data_end - 1] & 0xFF
                    if 1 <= last_byte <= 5:
                        return last_byte
            i += length + 1

        return None

    @staticmethod
    def bytes_to_hex(data: bytes) -> str:
        """Convert bytes to uppercase hex string."""
        return data.hex().upper()
