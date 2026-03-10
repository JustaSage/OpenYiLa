# OpenYiLa

[![Build](https://github.com/JustaSage/OpenYiLa/actions/workflows/build.yml/badge.svg)](https://github.com/JustaSage/OpenYiLa/actions/workflows/build.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)

Open-source command-line tool & Python library for controlling **YiLa (易拉) BLE door opener** devices.


## Features

- **Scan** — discover nearby YiLa BLE devices with battery level
- **Open** — send unlock command with configurable timing & direction
- **Password** — change device password over BLE
- **i18n** — English / 简体中文 / 繁體中文 (auto-detect or `OPENYILA_LANG`)
- **Cross-platform** — Linux, macOS, Windows; prebuilt binaries via GitHub Actions

## Install

### From source (requires Python ≥ 3.12)

```bash
# Using uv (recommended)
uv sync
uv run openyila --help

# Or using pip
pip install -e .
openyila --help
```

### Prebuilt binary

Download the latest release from [GitHub Releases](https://github.com/JustaSage/OpenYiLa/releases) — no Python required.

## CLI Usage

```bash
# Scan for nearby YiLa devices
openyila scan
openyila scan --timeout 10

# Unlock a device
openyila open AA:BB:CC:DD:EE:FF -p 123456

# Unlock with custom timing (ms) and reverse mode
openyila open AA:BB:CC:DD:EE:FF -p 123456 --open-time 800 --wait-time 3000 --reverse

# Change device password
openyila passwd AA:BB:CC:DD:EE:FF --old 123456 --new 654321

# Verbose logging
openyila -v open AA:BB:CC:DD:EE:FF -p 123456
```

## Library Usage

```python
import asyncio
from openyila import YilaDevice, YilaClient, YilaScanner

# Scan for devices
scanner = YilaScanner(scan_timeout=6.0)
devices = asyncio.run(scanner.scan())
for d in devices:
    print(f"{d['name']} [{d['address']}] RSSI={d['rssi']}")

# Unlock a door
device = YilaDevice(address="AA:BB:CC:DD:EE:FF", password="123456")
client = YilaClient(device)
response = asyncio.run(client.open_and_disconnect())
print(response.success, response.battery_level)
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
  Times in milliseconds (default: 500,500,500)
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

## Disclaimer

> **Legal Notice**
>>
> - This project is **not affiliated with, endorsed by, or associated with** YiLa or Shenzhen Xinghe Changlu Technology Corporation Limited.(深圳星河长路技术有限公司) in any way.
> - This software is distributed under the AGPL-3.0 license, **with absolutely no warranty**. Use at your own risk.
> - Users are responsible for ensuring compliance with local laws and regulations. The authors assume **no liability** for any consequences of using this software.
> - If the original rights holder has any concerns, please open an issue for communication.

## License

[AGPL-3.0](LICENSE)

## Device Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| password | — | 6 digits | Device access password |
| open_time | 500ms | 0-10000 | Open signal duration |
| wait_time | 500ms | 0-10000 | Pause between open and close |
| close_time | 500ms | 0-10000 | Close signal duration |
| attribute | 0 | 0 or 1 | 0=normal, 1=reverse |
