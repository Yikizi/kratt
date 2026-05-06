#!/usr/bin/env python3
"""Smoke test for BLE frame encoding format."""

from __future__ import annotations

from bridge import WIZ_BRIDGE_AUTO_TARGET_IP, WIZ_BRIDGE_SERVICE_UUID, build_wiz_frame


def test_frame_encoding() -> None:
    payload = {"method": "setPilot", "params": {"state": True, "dimming": 77}}
    frame = build_wiz_frame("192.168.2.100", payload)

    expected_prefix = bytes([192, 168, 2, 100, 151, 243])
    assert frame.startswith(expected_prefix)
    assert frame == expected_prefix + b'{"method":"setPilot","params":{"state":true,"dimming":77}}'


def test_auto_frame_encoding() -> None:
    payload = {"method": "setPilot", "params": {"state": False}}
    frame = build_wiz_frame(None, payload)

    expected_prefix = bytes([0, 0, 0, 0, 151, 243])
    assert WIZ_BRIDGE_AUTO_TARGET_IP == "0.0.0.0"
    assert frame == expected_prefix + b'{"method":"setPilot","params":{"state":false}}'


def main() -> None:
    test_frame_encoding()
    test_auto_frame_encoding()
    print("OK", WIZ_BRIDGE_SERVICE_UUID)


if __name__ == "__main__":
    main()
