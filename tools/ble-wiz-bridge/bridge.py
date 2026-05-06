#!/usr/bin/env python3
"""BLE client and wire-format helper for forwarding WiZ commands.

This module sends a binary frame over BLE GATT:

    [4 bytes target IPv4 BE][2 bytes UDP port BE][JSON payload]

where the payload is the WiZ UDP command. Target IP 0.0.0.0 means
"auto"; the ESP32 forwards to its learned WiZ bulb IP or broadcasts on the
AP subnet when no bulb has been learned yet.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import threading
from typing import Any, Mapping

try:
    from bleak import BleakClient, BleakScanner
except ImportError as exc:  # pragma: no cover
    BleakClient = BleakScanner = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

WIZ_BRIDGE_DEVICE_NAME = "Kratt-BLE-Bridge"
WIZ_BRIDGE_SERVICE_UUID = "c6d6f8f5-6b2d-6d4b-8f5d-0f1d2c3b4a50"
WIZ_BRIDGE_CHAR_UUID = "ada1a7c2-574b-4f2a-b6f7-9f8d0c4b2a11"
WIZ_BRIDGE_AUTO_TARGET_IP = "0.0.0.0"
WIZ_BRIDGE_DEFAULT_BULB_IP = WIZ_BRIDGE_AUTO_TARGET_IP
WIZ_UDP_PORT = 38899

logger = logging.getLogger(__name__)

_LOOP: asyncio.AbstractEventLoop | None = None
_LOOP_THREAD: threading.Thread | None = None
_CLIENT: BleakClient | None = None
_NOTIFY_STARTED = False
_LAST_NOTIFY_TEXT: str | None = None
_DISCOVER_TIMEOUT_S = 10.0
_CONNECTION_TIMEOUT_S = 10.0
_RESPONSE_READ_DELAY_S = 0.05
_SEND_LOCK = threading.Lock()


def build_wiz_frame(
    target_ip: str | None,
    payload: Mapping[str, Any],
    port: int = WIZ_UDP_PORT,
) -> bytes:
    """Build WiZ bridge frame bytes.

    target_ip may be None / "auto" / "0.0.0.0" to ask the ESP32 to use
    AP-subnet auto forwarding.
    """
    if target_ip is None or str(target_ip).strip().lower() == "auto":
        target_ip = WIZ_BRIDGE_AUTO_TARGET_IP
    ip = ipaddress.ip_address(target_ip)
    if ip.version != 4:
        raise ValueError(f"target_ip must be IPv4, got: {target_ip}")
    if not (0 < port <= 65535):
        raise ValueError(f"Invalid UDP port: {port}")

    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return ip.packed + port.to_bytes(2, "big") + body


def _start_loop() -> asyncio.AbstractEventLoop:
    global _LOOP, _LOOP_THREAD

    if _LOOP is not None:
        return _LOOP

    if BleakClient is None:
        raise RuntimeError(
            "bleak is not installed. Install via project environment dependencies (uv sync)."
        )

    loop = asyncio.new_event_loop()

    def _run() -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    _LOOP = loop
    _LOOP_THREAD = threading.Thread(target=_run, daemon=True, name="ble-wiz-loop")
    _LOOP_THREAD.start()
    return loop


def _run_async(coro, timeout: float = 25):
    loop = _start_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop).result(timeout=timeout)


async def _find_bridge_address() -> str:
    devices = await BleakScanner.discover(timeout=_DISCOVER_TIMEOUT_S, return_adv=True)
    iterable = devices.values() if isinstance(devices, dict) else [(dev, None) for dev in devices]

    for dev, adv in iterable:
        names = [dev.name]
        if adv is not None:
            names.append(getattr(adv, "local_name", None))
        if any(name == WIZ_BRIDGE_DEVICE_NAME for name in names if name):
            return dev.address

    iterable = devices.values() if isinstance(devices, dict) else [(dev, None) for dev in devices]
    for dev, adv in iterable:
        names = [dev.name]
        if adv is not None:
            names.append(getattr(adv, "local_name", None))
        if any(name and name.lower() == WIZ_BRIDGE_DEVICE_NAME.lower() for name in names):
            return dev.address

    raise RuntimeError(
        f"BLE bridge '{WIZ_BRIDGE_DEVICE_NAME}' not found. Scan timeout was {_DISCOVER_TIMEOUT_S}s."
    )


async def _ensure_client() -> BleakClient:
    global _CLIENT, _NOTIFY_STARTED

    if _CLIENT is not None and _CLIENT.is_connected:
        return _CLIENT

    if _CLIENT is not None:
        await _CLIENT.disconnect()
        _CLIENT = None
        _NOTIFY_STARTED = False

    address = await _find_bridge_address()
    logger.info("Connecting to BLE bridge at %s", address)
    client = BleakClient(address, timeout=_CONNECTION_TIMEOUT_S)
    await client.connect()

    services = client.services
    service = services.get_service(WIZ_BRIDGE_SERVICE_UUID)
    if service is None:
        await client.disconnect()
        raise RuntimeError(f"Service not found on bridge: {WIZ_BRIDGE_SERVICE_UUID}")

    char = service.get_characteristic(WIZ_BRIDGE_CHAR_UUID)
    if char is None:
        await client.disconnect()
        raise RuntimeError(f"Characteristic not found on bridge: {WIZ_BRIDGE_CHAR_UUID}")

    _CLIENT = client
    return client


def _decode_response(data: bytes | bytearray | str | None) -> dict[str, Any]:
    if data is None:
        return {"ok": True, "ble_write": True, "response_ok": False}
    if isinstance(data, str):
        text = data
    else:
        text = bytes(data).decode("utf-8", errors="replace")
    if not text:
        return {"ok": True, "ble_write": True, "response_ok": False}
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return {"ok": True, "ble_write": True, "raw": text, "response_ok": False}


def _notification_handler(sender: int, data: bytearray) -> None:
    global _LAST_NOTIFY_TEXT
    _LAST_NOTIFY_TEXT = bytes(data).decode("utf-8", errors="replace")
    logger.debug("BLE notify from %s: %s", sender, _LAST_NOTIFY_TEXT)


async def _ensure_notify(client: BleakClient) -> None:
    global _NOTIFY_STARTED
    if _NOTIFY_STARTED:
        return
    try:
        await client.start_notify(WIZ_BRIDGE_CHAR_UUID, _notification_handler)
        _NOTIFY_STARTED = True
    except Exception as exc:  # old firmware may not support notify; read still works on new firmware
        logger.debug("BLE notify unavailable: %s", exc)


async def _close_client() -> None:
    global _CLIENT, _NOTIFY_STARTED
    if _CLIENT is None:
        return
    try:
        await _CLIENT.disconnect()
    finally:
        _CLIENT = None
        _NOTIFY_STARTED = False


async def _send_payload(payload: bytes) -> None:
    client = await _ensure_client()
    await client.write_gatt_char(WIZ_BRIDGE_CHAR_UUID, payload, response=True)


async def _send_payload_with_response(payload: bytes) -> dict[str, Any]:
    client = await _ensure_client()
    await _ensure_notify(client)
    await client.write_gatt_char(WIZ_BRIDGE_CHAR_UUID, payload, response=True)

    # The firmware updates a readable characteristic synchronously in the write
    # handler. A tiny delay avoids racing BLE stacks that complete write before
    # their local read cache is refreshed.
    await asyncio.sleep(_RESPONSE_READ_DELAY_S)
    try:
        data = await client.read_gatt_char(WIZ_BRIDGE_CHAR_UUID)
        return _decode_response(data)
    except Exception as exc:
        logger.debug("BLE response read failed: %s", exc)
        return _decode_response(_LAST_NOTIFY_TEXT)


def warm_ble_bridge() -> bool:
    """Connect to the BLE bridge and keep the GATT client cached.

    This is used by the full demo during startup so the first wake-word action
    does not spend time scanning/connecting.
    """
    if _IMPORT_ERROR is not None:
        logger.error("bleak import failed: %s", _IMPORT_ERROR)
        return False

    try:
        with _SEND_LOCK:
            _run_async(_ensure_client())
        return True
    except Exception as exc:  # pragma: no cover
        logger.error("BLE warmup failed: %s", exc)
        _run_async(_close_client())
        return False


def send_wiz_via_ble(
    target_ip: str | None,
    payload: Mapping[str, Any],
    port: int = WIZ_UDP_PORT,
) -> bool:
    """Send a single WiZ command over BLE bridge.

    Returns True when write to characteristic succeeded, False otherwise.
    """
    if _IMPORT_ERROR is not None:
        logger.error("bleak import failed: %s", _IMPORT_ERROR)
        return False

    try:
        with _SEND_LOCK:
            frame = build_wiz_frame(target_ip, payload, port=port)
            _run_async(_send_payload(frame))
        return True
    except Exception as exc:  # pragma: no cover
        logger.error("BLE send failed: %s", exc)
        _run_async(_close_client())
        return False


def send_wiz_via_ble_response(
    target_ip: str | None,
    payload: Mapping[str, Any],
    port: int = WIZ_UDP_PORT,
) -> dict[str, Any] | None:
    """Send WiZ command and read the ESP32 firmware response summary.

    Returns a JSON-like dict from the readable BLE characteristic, or None when
    the BLE transaction itself failed.
    """
    if _IMPORT_ERROR is not None:
        logger.error("bleak import failed: %s", _IMPORT_ERROR)
        return None

    try:
        with _SEND_LOCK:
            frame = build_wiz_frame(target_ip, payload, port=port)
            return _run_async(_send_payload_with_response(frame))
    except Exception as exc:  # pragma: no cover
        logger.error("BLE send/read failed: %s", exc)
        _run_async(_close_client())
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send WiZ JSON over BLE bridge")
    parser.add_argument(
        "payload",
        help='Payload JSON object. Example: {"method":"setPilot","params":{"state":true}}',
    )
    parser.add_argument("--bulb", default=None, help="Target WiZ bulb IP (default: auto/broadcast)")
    parser.add_argument("--port", type=int, default=WIZ_UDP_PORT)
    parser.add_argument("--response", action="store_true", help="Read and print firmware response JSON")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    payload = json.loads(args.payload)
    if args.response:
        response = send_wiz_via_ble_response(args.bulb, payload, port=args.port)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        raise SystemExit(0 if response is not None else 1)
    ok = send_wiz_via_ble(args.bulb, payload, port=args.port)
    raise SystemExit(0 if ok else 1)
