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
import os
import threading
import time
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
_BRIDGE_ADDRESS: str | None = None
_CLIENT_CONNECTED_AT = 0.0
_CLIENT_LAST_USED_AT = 0.0
_NOTIFY_STARTED = False
_LAST_NOTIFY_TEXT: str | None = None
_DISCOVER_TIMEOUT_S = float(os.getenv("KRATT_BLE_DISCOVER_TIMEOUT_S", "10"))
_CONNECTION_TIMEOUT_S = float(os.getenv("KRATT_BLE_CONNECTION_TIMEOUT_S", "10"))
_OPERATION_TIMEOUT_S = float(os.getenv("KRATT_BLE_OPERATION_TIMEOUT_S", "18"))
_RESPONSE_READ_DELAY_S = float(os.getenv("KRATT_BLE_RESPONSE_READ_DELAY_S", "0.05"))
_RESPONSE_READ_ATTEMPTS = int(os.getenv("KRATT_BLE_RESPONSE_READ_ATTEMPTS", "5"))
_RETRY_ATTEMPTS = int(os.getenv("KRATT_BLE_RETRY_ATTEMPTS", "2"))
_RETRY_DELAY_S = float(os.getenv("KRATT_BLE_RETRY_DELAY_S", "0.25"))
_WRITE_WITH_RESPONSE = os.getenv("KRATT_BLE_WRITE_WITH_RESPONSE", "1").lower() in {
    "1", "true", "yes", "on"
}
_MAX_CONNECTION_AGE_S = float(os.getenv("KRATT_BLE_MAX_CONNECTION_AGE_S", "0"))
_MAX_IDLE_S = float(os.getenv("KRATT_BLE_MAX_IDLE_S", "20"))
_HEARTBEAT_INTERVAL_S = float(os.getenv("KRATT_BLE_HEARTBEAT_S", "2"))
_HEARTBEAT_TIMEOUT_S = float(os.getenv("KRATT_BLE_HEARTBEAT_TIMEOUT_S", "4"))
_TRACE_ENABLED = os.getenv("KRATT_BLE_TRACE", "1").lower() not in {"0", "false", "no", "off"}
_TRACE_PATH = os.getenv("KRATT_BLE_TRACE_FILE", "/tmp/kratt_ble_bridge_trace.jsonl")
_HEARTBEAT_THREAD: threading.Thread | None = None
_HEARTBEAT_STOP = threading.Event()
_TRACE_LOCK = threading.Lock()
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


def _trace(event: str, **fields: Any) -> None:
    if not _TRACE_ENABLED:
        return
    record = {
        "ts": time.time(),
        "mono": time.monotonic(),
        "event": event,
        **fields,
    }
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    try:
        with _TRACE_LOCK:
            with open(_TRACE_PATH, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception:
        pass


def _run_async(coro, timeout: float = _OPERATION_TIMEOUT_S):
    loop = _start_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    try:
        return future.result(timeout=timeout)
    except Exception:
        future.cancel()
        raise


def _start_heartbeat() -> None:
    """Keep the CoreBluetooth <-> ESP32 GATT session warm during demos."""
    global _HEARTBEAT_THREAD, _HEARTBEAT_STOP
    if _HEARTBEAT_INTERVAL_S <= 0:
        return
    if _HEARTBEAT_THREAD is not None and _HEARTBEAT_THREAD.is_alive():
        return
    if _HEARTBEAT_STOP.is_set():
        _HEARTBEAT_STOP = threading.Event()
    _HEARTBEAT_THREAD = threading.Thread(
        target=_heartbeat_worker,
        name="ble-wiz-heartbeat",
        daemon=True,
    )
    _HEARTBEAT_THREAD.start()
    _trace("heartbeat_started", interval_s=_HEARTBEAT_INTERVAL_S, trace_file=_TRACE_PATH)


def _stop_heartbeat() -> None:
    global _HEARTBEAT_THREAD
    _HEARTBEAT_STOP.set()
    if _HEARTBEAT_THREAD is not None and _HEARTBEAT_THREAD is not threading.current_thread():
        _HEARTBEAT_THREAD.join(timeout=1.0)
    _HEARTBEAT_THREAD = None
    _trace("heartbeat_stopped")


def _heartbeat_worker() -> None:
    while not _HEARTBEAT_STOP.wait(_HEARTBEAT_INTERVAL_S):
        if not _SEND_LOCK.acquire(timeout=0.05):
            _trace("heartbeat_skipped", reason="send_lock_busy")
            continue
        started = time.monotonic()
        try:
            _run_async(_heartbeat_once(), timeout=_HEARTBEAT_TIMEOUT_S)
            _trace("heartbeat_ok", duration_ms=int((time.monotonic() - started) * 1000))
        except Exception as exc:  # pragma: no cover - depends on live BLE stack
            _trace(
                "heartbeat_failed",
                duration_ms=int((time.monotonic() - started) * 1000),
                error=repr(exc),
            )
            logger.debug("BLE heartbeat failed; dropping cached client: %s", exc)
            try:
                _run_async(_close_client(), timeout=2)
            except Exception:
                pass
        finally:
            _SEND_LOCK.release()


async def _heartbeat_once() -> None:
    global _CLIENT_LAST_USED_AT
    client = await _ensure_client(start_heartbeat=False)
    await client.read_gatt_char(WIZ_BRIDGE_CHAR_UUID)
    _CLIENT_LAST_USED_AT = time.monotonic()


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


def _on_client_disconnected(client) -> None:
    global _CLIENT, _CLIENT_CONNECTED_AT, _CLIENT_LAST_USED_AT, _NOTIFY_STARTED
    logger.info("BLE bridge disconnected")
    _trace("client_disconnected")
    if client is _CLIENT:
        _CLIENT = None
        _CLIENT_CONNECTED_AT = 0.0
        _CLIENT_LAST_USED_AT = 0.0
        _NOTIFY_STARTED = False


async def _ensure_client(*, start_heartbeat: bool = True) -> BleakClient:
    global _CLIENT, _BRIDGE_ADDRESS, _CLIENT_CONNECTED_AT, _CLIENT_LAST_USED_AT, _NOTIFY_STARTED

    now = time.monotonic()
    if _CLIENT is not None and _CLIENT.is_connected:
        age_s = now - _CLIENT_CONNECTED_AT if _CLIENT_CONNECTED_AT else 0.0
        idle_s = now - _CLIENT_LAST_USED_AT if _CLIENT_LAST_USED_AT else 0.0
        if (
            (_MAX_CONNECTION_AGE_S > 0 and age_s > _MAX_CONNECTION_AGE_S)
            or (_MAX_IDLE_S > 0 and idle_s > _MAX_IDLE_S)
        ):
            logger.info(
                "BLE bridge connection is stale (age=%.1fs idle=%.1fs); reconnecting",
                age_s,
                idle_s,
            )
            _trace("client_stale", age_s=round(age_s, 3), idle_s=round(idle_s, 3))
            try:
                await _CLIENT.disconnect()
            except Exception as exc:
                logger.debug("BLE stale disconnect failed: %s", exc)
            _CLIENT = None
            _NOTIFY_STARTED = False
        else:
            return _CLIENT

    if _CLIENT is not None:
        try:
            await _CLIENT.disconnect()
        except Exception as exc:
            logger.debug("BLE disconnect before reconnect failed: %s", exc)
        _CLIENT = None
        _NOTIFY_STARTED = False

    if _BRIDGE_ADDRESS:
        address = _BRIDGE_ADDRESS
        scan_ms = 0
        _trace("connect_cached_address", address=address)
    else:
        scan_started = time.monotonic()
        address = await _find_bridge_address()
        scan_ms = int((time.monotonic() - scan_started) * 1000)
        _BRIDGE_ADDRESS = address
    logger.info("Connecting to BLE bridge at %s", address)
    _trace("connect_start", address=address, scan_ms=scan_ms)
    connect_started = time.monotonic()
    client = BleakClient(
        address,
        timeout=_CONNECTION_TIMEOUT_S,
        disconnected_callback=_on_client_disconnected,
    )
    try:
        await client.connect()
    except Exception:
        if _BRIDGE_ADDRESS == address:
            _BRIDGE_ADDRESS = None
        raise
    connect_ms = int((time.monotonic() - connect_started) * 1000)

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
    _CLIENT_CONNECTED_AT = time.monotonic()
    _CLIENT_LAST_USED_AT = _CLIENT_CONNECTED_AT
    _trace("connect_ok", address=address, scan_ms=scan_ms, connect_ms=connect_ms)
    if start_heartbeat:
        _start_heartbeat()
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
    global _CLIENT, _CLIENT_CONNECTED_AT, _CLIENT_LAST_USED_AT, _NOTIFY_STARTED
    if _CLIENT is None:
        return
    try:
        await _CLIENT.disconnect()
    finally:
        _CLIENT = None
        _CLIENT_CONNECTED_AT = 0.0
        _CLIENT_LAST_USED_AT = 0.0
        _NOTIFY_STARTED = False


def _expected_command_from_frame(payload: bytes) -> str:
    return payload[6:].decode("utf-8", errors="replace") if len(payload) >= 6 else ""


def _status_matches_command(status: dict[str, Any], expected_command: str) -> bool:
    if status.get("queued") is True:
        return False
    last_command = status.get("last_command")
    if not last_command or not expected_command:
        # Older firmware/status shapes may not expose last_command. Do not mark
        # those as stale purely because the field is missing.
        return True
    return str(last_command).strip() == expected_command.strip()


def _should_retry_status(status: dict[str, Any] | None, expected_command: str) -> bool:
    if status is None:
        return True
    if status.get("stale_status") is True:
        return True
    if not _status_matches_command(status, expected_command):
        return True
    # Current firmware reports udp_sent. If it is explicitly false, the write was
    # accepted by BLE but the ESP32 did not forward the UDP packet; retry once.
    if status.get("udp_sent") is False:
        return True
    return False


async def _send_payload(payload: bytes) -> None:
    global _CLIENT_LAST_USED_AT
    client = await _ensure_client()
    # With the async firmware, write-with-response is fast because the GATT
    # callback only queues the UDP work. Set KRATT_BLE_WRITE_WITH_RESPONSE=0 for
    # fire-and-forget diagnostics if a stale firmware still blocks on writes.
    started = time.monotonic()
    await client.write_gatt_char(
        WIZ_BRIDGE_CHAR_UUID,
        payload,
        response=_WRITE_WITH_RESPONSE,
    )
    _CLIENT_LAST_USED_AT = time.monotonic()
    _trace(
        "write_ok",
        response=_WRITE_WITH_RESPONSE,
        bytes=len(payload),
        duration_ms=int((_CLIENT_LAST_USED_AT - started) * 1000),
    )


async def _send_payload_with_response(payload: bytes) -> dict[str, Any]:
    global _CLIENT_LAST_USED_AT
    client = await _ensure_client()
    expected_command = _expected_command_from_frame(payload)
    write_started = time.monotonic()
    await client.write_gatt_char(WIZ_BRIDGE_CHAR_UUID, payload, response=True)
    _CLIENT_LAST_USED_AT = time.monotonic()
    _trace(
        "write_response_ok",
        bytes=len(payload),
        duration_ms=int((_CLIENT_LAST_USED_AT - write_started) * 1000),
    )

    # The firmware updates a readable characteristic synchronously in the write
    # handler. A tiny delay avoids racing BLE stacks that complete write before
    # their local read cache is refreshed. Do not subscribe to notifications on
    # the hot path; the readable characteristic is the authoritative status, and
    # extra CCCD traffic has made CoreBluetooth/NimBLE disconnect before.
    last_status: dict[str, Any] | None = None
    for attempt in range(max(1, _RESPONSE_READ_ATTEMPTS)):
        await asyncio.sleep(_RESPONSE_READ_DELAY_S * (attempt + 1))
        try:
            read_started = time.monotonic()
            data = await client.read_gatt_char(WIZ_BRIDGE_CHAR_UUID)
            status = _decode_response(data)
            _trace(
                "response_read",
                attempt=attempt + 1,
                duration_ms=int((time.monotonic() - read_started) * 1000),
                status_keys=sorted(status.keys()),
            )
        except Exception as exc:
            logger.debug("BLE response read failed: %s", exc)
            status = _decode_response(_LAST_NOTIFY_TEXT)
        last_status = status
        if _status_matches_command(status, expected_command):
            _trace("response_matched", attempt=attempt + 1)
            return status
        logger.debug(
            "BLE status did not match command yet (attempt=%d expected=%s got=%s)",
            attempt + 1,
            expected_command,
            status.get("last_command"),
        )

    if last_status is None:
        last_status = {"ok": False, "ble_write": True, "response_ok": False}
    last_status = dict(last_status)
    last_status["stale_status"] = True
    last_status["expected_command"] = expected_command
    return last_status


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


def close_ble_bridge() -> None:
    """Close the cached BLE client, if any, and stop the keepalive thread."""
    _stop_heartbeat()
    try:
        with _SEND_LOCK:
            _run_async(_close_client(), timeout=5)
    except Exception as exc:  # pragma: no cover
        logger.debug("BLE close failed: %s", exc)


def send_wiz_via_ble(
    target_ip: str | None,
    payload: Mapping[str, Any],
    port: int = WIZ_UDP_PORT,
) -> bool:
    """Send a single WiZ command over BLE bridge.

    Returns True when write to characteristic succeeded, False otherwise.
    Retries with a fresh BLE connection when CoreBluetooth/NimBLE goes stale.
    """
    if _IMPORT_ERROR is not None:
        logger.error("bleak import failed: %s", _IMPORT_ERROR)
        return False

    with _SEND_LOCK:
        frame = build_wiz_frame(target_ip, payload, port=port)
        attempts = max(1, _RETRY_ATTEMPTS)
        total_started = time.monotonic()
        _trace("send_start", target_ip=target_ip, port=port, bytes=len(frame), attempts=attempts)
        for attempt in range(1, attempts + 1):
            attempt_started = time.monotonic()
            try:
                if attempt > 1:
                    _run_async(_close_client())
                    time.sleep(_RETRY_DELAY_S)
                _run_async(_send_payload(frame))
                _trace(
                    "send_ok",
                    attempt=attempt,
                    attempt_ms=int((time.monotonic() - attempt_started) * 1000),
                    total_ms=int((time.monotonic() - total_started) * 1000),
                )
                return True
            except Exception as exc:  # pragma: no cover
                _trace(
                    "send_failed_attempt",
                    attempt=attempt,
                    attempt_ms=int((time.monotonic() - attempt_started) * 1000),
                    error=repr(exc),
                )
                if attempt < attempts:
                    logger.debug("BLE send failed; reconnecting and retrying (attempt %d/%d): %s", attempt, attempts, exc)
                else:
                    logger.warning("BLE send failed after %d attempt(s): %s", attempts, exc)
                _run_async(_close_client())
        _trace("send_failed", total_ms=int((time.monotonic() - total_started) * 1000))
        return False


def send_wiz_via_ble_response(
    target_ip: str | None,
    payload: Mapping[str, Any],
    port: int = WIZ_UDP_PORT,
) -> dict[str, Any] | None:
    """Send WiZ command and read the ESP32 firmware response summary.

    Returns a JSON-like dict from the readable BLE characteristic, or None when
    the BLE transaction itself failed. Retries stale/mismatched status with a
    fresh BLE connection so long-running demos do not get stuck on an old GATT
    session.
    """
    if _IMPORT_ERROR is not None:
        logger.error("bleak import failed: %s", _IMPORT_ERROR)
        return None

    with _SEND_LOCK:
        frame = build_wiz_frame(target_ip, payload, port=port)
        expected_command = _expected_command_from_frame(frame)
        attempts = max(1, _RETRY_ATTEMPTS)
        last_status: dict[str, Any] | None = None
        for attempt in range(1, attempts + 1):
            try:
                if attempt > 1:
                    _run_async(_close_client())
                    time.sleep(_RETRY_DELAY_S)
                status = _run_async(_send_payload_with_response(frame))
                last_status = status
                if not _should_retry_status(status, expected_command):
                    return status
                if attempt < attempts:
                    logger.debug(
                        "BLE command status looked stale/unsent; reconnecting and retrying (attempt %d/%d): %s",
                        attempt,
                        attempts,
                        status,
                    )
                else:
                    logger.warning("BLE command status stayed stale/unsent after %d attempt(s): %s", attempts, status)
            except Exception as exc:  # pragma: no cover
                if attempt < attempts:
                    logger.debug("BLE send/read failed; reconnecting and retrying (attempt %d/%d): %s", attempt, attempts, exc)
                else:
                    logger.warning("BLE send/read failed after %d attempt(s): %s", attempts, exc)
            _run_async(_close_client())
        return last_status


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
