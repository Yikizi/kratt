# ESP32 recorder WiZ BLE bridge

This recorder firmware can forward WiZ UDP frames over BLE when the laptop and WiZ bulb are on different subnets.

## Topology

```text
MacBook CLI  --BLE GATT-->  ESP32 AP (Kratt-Recorder)
                               |
                               | UDP 38899 on AP subnet
                               |
                               v
                          WiZ bulb
```

The MacBook does **not** need to join the ESP32 Wi-Fi network. The bulb must join the ESP32 AP (`Kratt-Recorder` / `kuulekratt`). A phone/laptop may also join the same AP for the captive recorder UI.

## BLE frame format

Writes to the WiZ bridge characteristic use:

```text
[4 bytes target IPv4, big-endian][2 bytes UDP port, big-endian][JSON payload UTF-8]
```

The bridge strips the 6-byte routing header and forwards only the JSON payload.

Target IP semantics:

| Target in frame | Firmware behavior |
|---|---|
| `0.0.0.0` | Auto mode. If a WiZ responder IP has already been learned, send unicast to it; otherwise send one AP-subnet broadcast, e.g. `192.168.4.255:38899`, and learn the first responder. This is the default. |
| Concrete IPv4 | Send unicast to that AP-side IP. |

Stable IDs:

- Device name: `Kratt-BLE-Bridge`
- Service UUID: `c6d6f8f5-6b2d-6d4b-8f5d-0f1d2c3b4a50`
- Characteristic UUID: `ada1a7c2-574b-4f2a-b6f7-9f8d0c4b2a11`

These are defined in `main/ble_wiz_bridge.h` and `tools/ble-wiz-bridge/bridge.py`.

## DHCP / finding devices

Static single-IP DHCP is intentionally not used: the captive recorder UI may need a second client on the AP.

The firmware logs AP DHCP assignments:

```text
Client connected: aa:bb:cc:dd:ee:ff
DHCP lease: aa:bb:cc:dd:ee:ff -> 192.168.4.2
```

Use those logs if you want to learn the bulb IP/MAC. For normal one-bulb demo use, no IP is needed because the CLI defaults to auto mode. After forwarding a UDP command, the bridge also listens briefly for WiZ UDP replies, logs responder IPs, and caches the latest responder for later auto-unicast:

```text
WiZ UDP response from 192.168.4.2:38899 bytes=... first={...}
```

## Build / flash

```bash
cd hardware/esp32/firmware/recorder
idf.py build
idf.py flash monitor
```

If an old ignored `sdkconfig` already exists from a pre-BLE build, it may still contain `# CONFIG_BT_ENABLED is not set`; regenerate it or enable Bluetooth/NimBLE in menuconfig before flashing. A non-destructive compile check can use a temporary sdkconfig:

```bash
idf.py -B /tmp/kratt-recorder-ble-build \
  -DSDKCONFIG=/tmp/kratt-recorder-ble-sdkconfig build
```

Expected boot logs:

```text
WiFi AP started: SSID=Kratt-Recorder ...
BLE advertising started as 'Kratt-BLE-Bridge'
NimBLE initialized: service=c6d6f8f5-... char=ada1a7c2-...
```

## Python command sanity checks

Smoke test helpers:

```bash
python3 tools/ble-wiz-bridge/test_frame.py
./cli/kratt ble-wiz --on
./cli/kratt ble-wiz --off
```

`--on/--off` default to auto/broadcast (`0.0.0.0` in the BLE frame). Use `--bulb <ip>` only when you want explicit AP-side unicast.

## Demo pipeline

Prefer LAN/LAN `kratt demo --wiz` when available. Use BLE bridge fallback when using the ESP32 AP subnet:

```bash
./cli/kratt demo --wiz --ble-bridge --no-wakeword
```

When no `--bulbs` are provided, demo uses auto/broadcast.

## Troubleshooting

- BLE bridge not visible: ensure `CONFIG_BT_*` and `CONFIG_ESP_WIFI_SOFTAP_SUPPORT` are enabled and flash logs show `Kratt-BLE-Bridge`.
- Bulb no response in auto mode: confirm the bulb is joined to `Kratt-Recorder`, and monitor logs show a DHCP lease for it.
- Multiple WiZ bulbs on the AP: auto/broadcast may affect all bulbs; use `--bulb <ip>` for explicit unicast.
- `bleak` missing: install environment deps via project manifest and use the project venv.
- Command visibly works but `kratt ble-wiz --response` says `disconnected` / no confirmation: flash a build with the BLE write-stack fix (`sdkconfig.defaults` raises the NimBLE host task stack and `ble_wiz_bridge.c` keeps large response buffers off the NimBLE stack). Validate with `kratt ble-wiz --status --response`; it should return JSON with `udp_sent` and, when the bulb replies, `response_ok`.
