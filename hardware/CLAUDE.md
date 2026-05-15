# hardware/

Wake word deployment on physical devices.

## Structure

```
hardware/
├── esp32/
│   ├── esphome/                    # ESPHome configs for voice satellites
│   │   ├── voice-satellite-esp32-s3.yaml
│   │   ├── voice-satellite-esp32-s3-korvo2.yaml
│   │   ├── voice-satellite-esp32-s3-korvo2-demo.yaml
│   │   ├── models/kratt.json       # microWakeWord model manifest
│   │   └── secrets.yaml.example
│   └── firmware/                   # ESP-IDF C firmware
│       ├── components/kratt_korvo2/  # Board support (buttons, codec)
│       ├── recorder/               # WAV recorder for data collection
│       ├── logger/                 # Wake word event logger
│       ├── mic-test/               # I2S mic verification
│       ├── speaker-test/           # DAC/speaker check
│       ├── slideshow-clicker/      # BLE HID clicker (demo utility)
│       ├── korvo-serial-streamer/  # Korvo-2 mic → USB serial PCM for Python demo
│       └── wake-word-logger/       # Standalone wake word trigger logger
│
└── raspberry-pi/
    └── (planned: Wyoming satellite service)
```

## Key facts

- Primary board: ESP32-S3 Korvo-2 (dual mic, onboard codec)
- Framework: ESPHome for voice satellites, ESP-IDF for custom firmware
- Model format: TFLite INT8 via microWakeWord (~55KB-148KB for current models)
- Flash: `esphome run voice-satellite-esp32-s3-korvo2.yaml` or `./cli/kratt flash <model>`
- Wyoming protocol on port 10400

## Dev workflow

```bash
# ESPHome (voice satellite)
(cd hardware/esp32/esphome && esphome run voice-satellite-esp32-s3-korvo2.yaml)

# ESP-IDF firmware (e.g. recorder)
(cd hardware/esp32/firmware/recorder && idf.py build flash monitor)

# Korvo-2 mic as Python demo input
./cli/kratt korvo-streamer --flash --port /dev/cu.usbserial-2130
./cli/kratt demo --audio-source korvo-serial --serial-port /dev/cu.usbserial-2130
```
