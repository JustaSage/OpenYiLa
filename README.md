# OpenYila

Python library for controlling YiLa (易拉) BLE door opener devices.

Reverse-engineered from the Android app `com.macronum.bledemo` (易拉开门助手 v2.4).

## Install

```bash
pip install -e .
```

## CLI Usage

```bash
# Scan for YiLa devices
openyila scan

# Add a device
openyila add AA:BB:CC:DD:EE:FF -p 123456 -n "Front Door"

# Open a single device
openyila open AA:BB:CC:DD:EE:FF

# Open all saved devices
openyila open-all

# List saved devices
openyila list

# Change device password (over BLE)
openyila passwd AA:BB:CC:DD:EE:FF 654321

# Update device config
openyila config AA:BB:CC:DD:EE:FF --open-time 800 --wait-time 3000

# Remove a device
openyila remove AA:BB:CC:DD:EE:FF
```

## Library Usage

```python
import asyncio
from openyila import YilaDevice, YilaClient, YilaScanner, DeviceStore

# Scan
scanner = YilaScanner()
devices = asyncio.run(scanner.scan())

# Open a door
device = YilaDevice(address="AA:BB:CC:DD:EE:FF", password="123456")
client = YilaClient(device)
response = asyncio.run(client.open_and_disconnect())
print(response.success, response.message)

# Local storage
store = DeviceStore()
store.add(device)
all_devices = store.get_all()
```

## Protocol

Communication uses the Nordic UART Service (NUS) over BLE:

| UUID | Role |
|------|------|
| `6e400001-b5a3-f393-e0a9-e50e24dcca9e` | Service |
| `6e400002-b5a3-f393-e0a9-e50e24dcca9e` | TX (phone → device, write-no-response) |
| `6e400003-b5a3-f393-e0a9-e50e24dcca9e` | RX (device → phone, notify) |

### Command Encryption

1. Derive key from password: `MD5(password)[8:24]` (16 hex chars)
2. Build plaintext: `"{unix_timestamp}{key}{payload}"`
3. Pad to 16-byte boundary (zero-pad)
4. AES/ECB encrypt with fixed key `Fx4k6AWivOsLE4NI`

### Commands

**Open (unlock):**
```
Payload: "A:OPEN;P:{+|-} {openTime},{waitTime},{closeTime};"
  + = normal mode, - = reverse mode
  Times in milliseconds
```

**Change password:**
```
Payload: "A:PW;P:{MD5(new_password)[8:24]};"
  Encrypted with old password's derived key
```

### Response

- `OK` — success
- `ERROR` — password incorrect
- Single byte `1`-`5` — battery level (1=low, 5=full)

## Device Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| password | — | 6 digits | Device access password |
| open_time | 650ms | 0-10000 | Open signal duration |
| wait_time | 2000ms | 0-10000 | Pause between open and close |
| close_time | 650ms | 0-10000 | Close signal duration |
| attribute | 0 | 0 or 1 | 0=normal, 1=reverse |
