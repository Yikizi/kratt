# Firmware QoL Backlog — cleared 2026-05-05

Status: implemented in build label `recorder-qol-ble-wiz-2026-05-05`.

Implemented:
- captive portal WiZ lamp controls at `http://192.168.4.1`
- `/api/wiz/*` endpoints for on/off, brightness, color, temp, status/getPilot, broadcast discover, clear learned IP
- shared WiZ UDP helper with auto/broadcast + learned unicast target
- BLE bridge read/notify response path
- real `getPilot` state query support for portal, `kratt ble-wiz --status --response`, and BLE demo state responses
- portal diagnostics: AP IP/SSID, max/connected clients, recent DHCP leases, learned WiZ IP/status, BLE state, firmware label
- captive portal UI polish and setup checklist

Build: `idf.py build` succeeds. Flash pending until an ESP32 serial port is visible.
