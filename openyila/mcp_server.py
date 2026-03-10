"""MCP server for OpenYila, exposed over stdio transport."""

from openyila.client import YilaClient, open_device
from openyila.device import YilaDevice
from openyila.scanner import YilaScanner

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise RuntimeError(
        "The 'mcp' package is required for MCP server support. "
        "Install dependencies and retry."
    ) from exc


def _validate_password(password: str):
    if len(password) != 6 or not password.isdigit():
        raise ValueError("Password must be 6 digits")


_server = FastMCP("openyila")


@_server.tool()
async def scan_devices(timeout: float = 6.0) -> list[dict[str, object]]:
    """Scan nearby YiLa BLE devices."""
    scanner = YilaScanner(scan_timeout=timeout)
    devices = await scanner.scan()
    return devices


@_server.tool()
async def open_device_lock(
    address: str,
    password: str,
    open_time: int = 500,
    wait_time: int = 500,
    close_time: int = 500,
    reverse: bool = False,
) -> dict[str, object]:
    """Open a YiLa lock device."""
    _validate_password(password)
    device = YilaDevice(
        address=address,
        password=password,
        open_time=open_time,
        wait_time=wait_time,
        close_time=close_time,
        attribute=1 if reverse else 0,
    )
    response = await open_device(device)
    return {
        "success": response.success,
        "battery_level": response.battery_level,
        "message": response.message,
    }


@_server.tool()
async def change_device_password(address: str, old_password: str, new_password: str) -> dict[str, object]:
    """Change YiLa device password."""
    _validate_password(old_password)
    _validate_password(new_password)
    device = YilaDevice(address=address, password=old_password)
    client = YilaClient(device)
    try:
        await client.connect()
        response = await client.change_password(old_password, new_password)
    finally:
        await client.disconnect()
    return {
        "success": response.success,
        "battery_level": response.battery_level,
        "message": response.message,
    }


def run_mcp_server():
    """Start the OpenYila MCP server over stdio."""
    _server.run()
