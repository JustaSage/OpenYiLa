"""Internationalization support for OpenYila.

Locale detection order:
  1. OPENYILA_LANG environment variable (e.g. "en", "zh_CN", "zh_TW")
  2. System locale (LANG / LC_ALL / LC_MESSAGES)
  3. Fallback to "en"
"""

import locale
import os

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # ── CLI ───────────────────────────────────────────────────────────
        "app.help": "YiLa BLE access control tool",
        "opt.verbose": "Verbose logging",
        "opt.timeout": "Scan duration (seconds)",
        "cmd.scan": "Scan for nearby YiLa BLE devices.",
        "cmd.open": "Send unlock command to a device.",
        "cmd.passwd": "Change device password via BLE.",
        "cmd.mcp": "Start MCP server over stdio.",
        "arg.address": "Device Bluetooth address",
        "opt.password": "6-digit numeric password",
        "opt.open_time": "Open signal duration (ms)",
        "opt.wait_time": "Wait duration (ms)",
        "opt.close_time": "Close signal duration (ms)",
        "opt.reverse": "Reverse mode",
        "opt.old_password": "Current 6-digit password",
        "opt.new_password": "New 6-digit password",
        # scan
        "scan.scanning": "Scanning for YiLa devices ({timeout}s)...",
        "scan.no_devices": "No YiLa devices found",
        "scan.found": "\nFound {count} device(s):",
        "scan.battery": " Battery={level}",
        # open
        "open.success": "Unlock success: {address}",
        "open.battery": "  Battery level: {level}/5",
        "open.failed": "Unlock failed: {message}",
        # passwd
        "passwd.success": "Password changed: {address}",
        "passwd.failed": "Password change failed: {message}",
        # banner
        "banner": "This is free software licensed under AGPL-3.0, and comes with ABSOLUTELY NO WARRANTY.\nYou may redistribute it under the terms of the GNU Affero General Public License v3.",
        # errors
        "err.password_format": "Error: Password must be 6 digits",
        # ── client ────────────────────────────────────────────────────────
        "client.recv": "Response received: %s (hex: %s)",
        "client.connecting": "Connecting: %s (%s)",
        "client.no_nus": "Device {address} does not support Nordic UART Service",
        "client.connected": "Device connected: %s",
        "client.disconnected": "Device disconnected: %s",
        "client.not_connected": "Device not connected",
        "client.sending": "Sending command: %s",
        "client.timeout": "Device response timeout",
        "client.unlocking": "Unlock: %s (mode=%s, open=%dms, wait=%dms, close=%dms)",
        "client.mode_reverse": "reverse",
        "client.mode_normal": "normal",
        "client.password_invalid": "Password must be 6 digits",
        "client.changing_pwd": "Changing password: %s",
        # ── scanner ───────────────────────────────────────────────────────
        "scanner.found": "Found device: %s (%s) RSSI=%d battery=%s",
        # ── protocol ─────────────────────────────────────────────────────
        "proto.empty": "Empty response",
        "proto.pwd_error": "Password error",
        "proto.unknown": "Unknown response",
        # ── device ────────────────────────────────────────────────────────
        "bat.low": "Low battery, please charge",
        "bat.25": "Battery ~25%",
        "bat.50": "Battery ~50%",
        "bat.75": "Battery ~75%",
        "bat.100": "Battery ~100%",
        "bat.unknown": "Battery unknown",
    },
    "zh_CN": {
        "app.help": "YiLa BLE 门禁控制工具",
        "opt.verbose": "详细日志输出",
        "opt.timeout": "扫描时间(秒)",
        "cmd.scan": "扫描附近的 YiLa BLE 设备。",
        "cmd.open": "向指定设备发送开锁命令。",
        "cmd.passwd": "通过 BLE 修改设备密码。",
        "cmd.mcp": "通过 stdio 启动 MCP 服务器。",
        "arg.address": "设备蓝牙地址",
        "opt.password": "6位数字密码",
        "opt.open_time": "开信号时长(ms)",
        "opt.wait_time": "等待时长(ms)",
        "opt.close_time": "关信号时长(ms)",
        "opt.reverse": "反向模式",
        "opt.old_password": "当前6位数字密码",
        "opt.new_password": "新的6位数字密码",
        "scan.scanning": "扫描 YiLa 设备中 ({timeout}秒)...",
        "scan.no_devices": "未发现 YiLa 设备",
        "scan.found": "\n发现 {count} 个设备:",
        "scan.battery": " 电量={level}",
        "open.success": "开锁成功: {address}",
        "open.battery": "  电量等级: {level}/5",
        "open.failed": "开锁失败: {message}",
        "passwd.success": "密码修改成功: {address}",
        "passwd.failed": "密码修改失败: {message}",
        "banner": "本程序是自由软件，以 AGPL-3.0 协议发布，不附带任何担保。\n您可以在 GNU Affero 通用公共许可证第三版的条款下自由传播和修改本程序。",
        "err.password_format": "错误: 密码必须是6位数字",
        "client.recv": "收到设备响应: %s (hex: %s)",
        "client.connecting": "连接设备: %s (%s)",
        "client.no_nus": "设备 {address} 不支持 Nordic UART Service",
        "client.connected": "设备已连接并就绪: %s",
        "client.disconnected": "已断开设备: %s",
        "client.not_connected": "设备未连接",
        "client.sending": "发送命令: %s",
        "client.timeout": "设备响应超时",
        "client.unlocking": "开锁: %s (模式=%s, 开=%dms, 等=%dms, 关=%dms)",
        "client.mode_reverse": "反向",
        "client.mode_normal": "正常",
        "client.password_invalid": "密码必须是6位数字",
        "client.changing_pwd": "修改密码: %s",
        "scanner.found": "发现设备: %s (%s) RSSI=%d battery=%s",
        "proto.empty": "空响应",
        "proto.pwd_error": "密码错误",
        "proto.unknown": "未知响应",
        "bat.low": "电量低，请及时充电",
        "bat.25": "电量约25%",
        "bat.50": "电量约50%",
        "bat.75": "电量约75%",
        "bat.100": "电量约100%",
        "bat.unknown": "电量未知",
    },
    "zh_TW": {
        "app.help": "YiLa BLE 門禁控制工具",
        "opt.verbose": "詳細日誌輸出",
        "opt.timeout": "掃描時間(秒)",
        "cmd.scan": "掃描附近的 YiLa BLE 裝置。",
        "cmd.open": "向指定裝置發送開鎖命令。",
        "cmd.passwd": "透過 BLE 修改裝置密碼。",
        "cmd.mcp": "透過 stdio 啟動 MCP 伺服器。",
        "arg.address": "裝置藍牙位址",
        "opt.password": "6位數字密碼",
        "opt.open_time": "開信號時長(ms)",
        "opt.wait_time": "等待時長(ms)",
        "opt.close_time": "關信號時長(ms)",
        "opt.reverse": "反向模式",
        "opt.old_password": "目前6位數字密碼",
        "opt.new_password": "新的6位數字密碼",
        "scan.scanning": "掃描 YiLa 裝置中 ({timeout}秒)...",
        "scan.no_devices": "未發現 YiLa 裝置",
        "scan.found": "\n發現 {count} 個裝置:",
        "scan.battery": " 電量={level}",
        "open.success": "開鎖成功: {address}",
        "open.battery": "  電量等級: {level}/5",
        "open.failed": "開鎖失敗: {message}",
        "passwd.success": "密碼修改成功: {address}",
        "passwd.failed": "密碼修改失敗: {message}",
        "banner": "本程式是自由軟體，以 AGPL-3.0 協議發佈，不附帶任何擔保。\n您可以在 GNU Affero 通用公共授權條款第三版下自由傳播和修改本程式。",
        "err.password_format": "錯誤: 密碼必須是6位數字",
        "client.recv": "收到裝置回應: %s (hex: %s)",
        "client.connecting": "連接裝置: %s (%s)",
        "client.no_nus": "裝置 {address} 不支援 Nordic UART Service",
        "client.connected": "裝置已連接並就緒: %s",
        "client.disconnected": "已斷開裝置: %s",
        "client.not_connected": "裝置未連接",
        "client.sending": "發送命令: %s",
        "client.timeout": "裝置回應逾時",
        "client.unlocking": "開鎖: %s (模式=%s, 開=%dms, 等=%dms, 關=%dms)",
        "client.mode_reverse": "反向",
        "client.mode_normal": "正常",
        "client.password_invalid": "密碼必須是6位數字",
        "client.changing_pwd": "修改密碼: %s",
        "scanner.found": "發現裝置: %s (%s) RSSI=%d battery=%s",
        "proto.empty": "空回應",
        "proto.pwd_error": "密碼錯誤",
        "proto.unknown": "未知回應",
        "bat.low": "電量低，請及時充電",
        "bat.25": "電量約25%",
        "bat.50": "電量約50%",
        "bat.75": "電量約75%",
        "bat.100": "電量約100%",
        "bat.unknown": "電量未知",
    },
}

_LOCALE_MAP = {
    "zh": "zh_CN",
    "zh_cn": "zh_CN",
    "zh_hans": "zh_CN",
    "zh_sg": "zh_CN",
    "zh_tw": "zh_TW",
    "zh_hant": "zh_TW",
    "zh_hk": "zh_TW",
    "zh_mo": "zh_TW",
}


def _detect_lang() -> str:
    raw = os.environ.get("OPENYILA_LANG", "").strip()
    if not raw:
        # locale.getlocale() works on all platforms (getdefaultlocale deprecated)
        try:
            raw = locale.getlocale()[0] or ""
        except ValueError:
            raw = ""
    if not raw and os.name == "nt":
        # Windows: use GetUserDefaultUILanguage via ctypes
        try:
            import ctypes
            lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()  # type: ignore[attr-defined]
            # LCID → language: 0x0804=zh_CN, 0x0404=zh_TW, 0x0C04=zh_HK
            _LCID_MAP = {
                0x0804: "zh_CN", 0x1004: "zh_CN",  # zh-CN, zh-SG
                0x0404: "zh_TW", 0x0C04: "zh_TW", 0x1404: "zh_TW",  # zh-TW, zh-HK, zh-MO
            }
            raw = _LCID_MAP.get(lcid, "")
        except Exception:
            pass
    lang = raw.split(".")[0].replace("-", "_").lower()
    if lang in _LOCALE_MAP:
        return _LOCALE_MAP[lang]
    if lang in _TRANSLATIONS:
        return lang
    prefix = lang.split("_")[0]
    if prefix in _LOCALE_MAP:
        return _LOCALE_MAP[prefix]
    return "en"


_current_lang: str = _detect_lang()
_strings: dict[str, str] = _TRANSLATIONS[_current_lang]


def t(key: str, **kwargs: object) -> str:
    """Get translated string, with optional {name} placeholder formatting."""
    msg = _strings.get(key) or _TRANSLATIONS["en"].get(key, key)
    return msg.format(**kwargs) if kwargs else msg


def get_lang() -> str:
    """Return the active language code."""
    return _current_lang
