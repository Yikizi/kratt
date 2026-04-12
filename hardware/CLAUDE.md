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
│       └── wake-word-logger/       # Standalone wake word trigger logger
│
└── raspberry-pi/
    └── (planned: Wyoming satellite service)
```

## Key facts

- Primary board: ESP32-S3 Korvo-2 (dual mic, onboard codec)
- Framework: ESPHome for voice satellites, ESP-IDF for custom firmware
- Model format: TFLite INT8 via microWakeWord (~56KB per model)
- Flash: `esphome run voice-satellite-esp32-s3-korvo2.yaml`
- Wyoming protocol on port 10400

## Dev workflow

```bash
# ESPHome (voice satellite)
(cd hardware/esp32/esphome && esphome run voice-satellite-esp32-s3-korvo2.yaml)

# ESP-IDF firmware (e.g. recorder)
(cd hardware/esp32/firmware/recorder && idf.py build flash monitor)
```
