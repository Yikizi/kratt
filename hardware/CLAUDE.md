# Hardware Implementations

**Context**: Oled `kratt/hardware/` kaustas - siin on wake word deployment ESP32 ja Raspberry Pi peale.

## 🎯 Mis See On?

Siin on kood ja konfiguratsioonid wake word'i jooksutamiseks:
- **ESP32C3 Supermini** - odav, väike, embedded
- **Raspberry Pi** - võimsam, Python-friendly

## 📁 Struktuur

```
hardware/
├── esp32/
│   ├── esphome/
│   │   ├── voice-satellite.yaml      # ESPHome config
│   │   ├── secrets.yaml.example      # Template
│   │   └── kratt-microww.tflite      # Wake word mudel
│   ├── firmware/                      # Custom firmware (if needed)
│   └── schematics/
│       └── wiring-diagram.md          # INMP441 connections
│
└── raspberry-pi/
    ├── wyoming/
    │   ├── wyoming-satellite.py       # Wyoming server
    │   ├── config.yaml                # Configuration
    │   └── kratt-openww.onnx          # Wake word mudel
    ├── systemd/
    │   └── wyoming-kratt.service      # Auto-start
    └── setup-scripts/
        └── install.sh                 # One-click setup
```

## 🔌 ESP32C3 Supermini

### Hardware Specs
```
CPU:        160MHz RISC-V single-core (ESP32-C3)
RAM:        400KB SRAM
Flash:      4MB
WiFi:       802.11 b/g/n (2.4GHz)
Bluetooth:  5.0 LE
Cost:       ~€5
Power:      ~100mA @ 5V (active)
```

### Wake Word Performance
```
Model:      kratt-microww.tflite (~200KB)
RAM usage:  ~100-150KB (active)
Latency:    200-500ms
Accuracy:   ~95% (with good training data)
```

### Wiring (INMP441 I2S Microphone)
```
INMP441          ESP32C3
-------          -------
SCK      →       GPIO5 (I2S BCLK)
WS       →       GPIO4 (I2S LRCLK)
SD       →       GPIO6 (I2S DIN)
L/R      →       GND (mono)
VDD      →       3.3V
GND      →       GND
```

### ESPHome Configuration
```yaml
# esphome/voice-satellite.yaml
micro_wake_word:
  models:
    - model: /config/esphome/kratt-microww.tflite
      probability_cutoff: 0.5  # Tune based on testing
      sliding_window_average_size: 10

  on_wake_word_detected:
    - voice_assistant.start:
        wake_word: "Kratt"
```

### Deployment
```bash
# Flash from Mac
cd ~/kratt/hardware/esp32/esphome
esphome run voice-satellite.yaml

# Monitor
esphome logs voice-satellite.yaml
```

## 🍓 Raspberry Pi

### Hardware Specs (Pi 5)
```
CPU:        4× 2.4GHz ARM Cortex-A76
RAM:        8GB LPDDR4X
Storage:    microSD (128GB+)
WiFi:       802.11 ac (5GHz)
Cost:       ~€100
Power:      ~15W
```

### Wake Word Performance
```
Model:      kratt-openww.onnx (~2-5MB)
RAM usage:  ~100MB
Latency:    100-200ms (faster than ESP32!)
Accuracy:   ~97-99% (better than ESP32)
```

### Wyoming Server Setup
```bash
# Install
cd ~/kratt/hardware/raspberry-pi/setup-scripts
./install.sh

# Start manually
cd ~/kratt/hardware/raspberry-pi/wyoming
python wyoming-satellite.py --uri tcp://0.0.0.0:10400

# Or use systemd
sudo systemctl enable wyoming-kratt
sudo systemctl start wyoming-kratt
```

### Configuration
```yaml
# wyoming/config.yaml
wake_word:
  model: ./kratt-openww.onnx
  threshold: 0.5
  window_size: 10

audio:
  sample_rate: 16000
  channels: 1
  format: s16le

wyoming:
  uri: tcp://0.0.0.0:10400
```

## 🔗 Integration with Home Assistant

Both implementations expose Wyoming protocol:
```
ESP32:          tcp://<esp32-ip>:10400
Raspberry Pi:   tcp://127.0.0.1:10400  (if running on same Pi as HA)
```

Home Assistant configuration:
```yaml
# configuration.yaml
wyoming:
  - platform: satellite
    name: "Kratt Voice Satellite (ESP32)"
    uri: "tcp://192.168.1.50:10400"
    wake_word: "kratt"

  - platform: satellite
    name: "Kratt Voice Satellite (Pi)"
    uri: "tcp://127.0.0.1:10400"
    wake_word: "kratt"
```

## 📊 Comparison

| Feature | ESP32C3 | Raspberry Pi 5 |
|---------|---------|----------------|
| **Cost** | €5-10 | €100 |
| **Power** | 0.5W | 15W |
| **Size** | Tiny (thumb) | Deck of cards |
| **Setup** | ESPHome (easy) | Python (medium) |
| **Accuracy** | 95% | 97-99% |
| **Latency** | 200-500ms | 100-200ms |
| **RAM** | 150KB | 100MB |
| **Model** | 200KB TFLite | 2-5MB ONNX |
| **Use Case** | Distributed satellites | Central hub |

## 🎯 Recommended Setup

### Single Room (Budget)
```
1× Raspberry Pi 5 (HA + STT + Wake Word)
Cost: ~€120
```

### Whole House (Optimal)
```
1× Raspberry Pi 5 (HA + STT)
3-5× ESP32C3 (Wake Word satellites in each room)
Cost: ~€135-155
```

## 🐛 Troubleshooting

### ESP32
```bash
# Check logs
esphome logs voice-satellite.yaml

# Common issues:
# - WiFi not connecting: Check secrets.yaml
# - Mic not working: Check wiring (especially GND!)
# - Wake word not detecting: Tune probability_cutoff
# - Memory errors: Model too large, reduce size
```

### Raspberry Pi
```bash
# Check service
sudo systemctl status wyoming-kratt

# Check logs
journalctl -u wyoming-kratt -f

# Test manually
python wyoming-satellite.py --debug

# Common issues:
# - Port already in use: Stop other Wyoming services
# - Model not loading: Check file path and permissions
# - High CPU usage: Reduce model complexity
```

## 📝 Thesis Documentation

For each implementation, document:
- Hardware specifications
- Performance metrics (latency, accuracy, power)
- Setup complexity
- Cost analysis
- Trade-offs and recommendations

Include photos/diagrams of physical setup!

## 🚀 Deployment Checklist

### ESP32
- [ ] Order INMP441 microphones (€2-3 each)
- [ ] Flash ESPHome firmware
- [ ] Upload wake word model
- [ ] Test wake word detection
- [ ] Tune threshold based on testing
- [ ] Mount in permanent location
- [ ] Document wiring and setup

### Raspberry Pi
- [ ] Install Python dependencies
- [ ] Copy wake word model
- [ ] Configure Wyoming service
- [ ] Test with Home Assistant
- [ ] Set up auto-start (systemd)
- [ ] Monitor resource usage
- [ ] Document performance

---

**Parallel Development**: Töötad Pi-l, kuna sul on USB mic. ESP32 tulebpärast, kui mic'id kohale jõuavad (1-2 nädalat).
