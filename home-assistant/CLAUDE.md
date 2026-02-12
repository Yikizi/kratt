# Home Assistant Integration

**Context**: Oled `kratt/home-assistant/` kaustas - HA integratsioon ja addon.

## 🎯 Mis See On?

Siin on kood, mis muudab "Kratt" wake word'i Home Assistanti add-on'iks, mida teised kasutajad saavad installida.

## 📁 Struktuur

```
home-assistant/
├── addon/                     # HA Add-on package
│   ├── config.yaml            # Add-on metadata
│   ├── Dockerfile             # Container build
│   ├── run.sh                 # Entry point
│   ├── rootfs/                # Filesystem overlay
│   │   └── etc/
│   └── README.md              # Add-on documentation
│
├── custom-component/          # (Optional) Custom integration
└── configurations/            # Example configs
    └── voice-pipeline.yaml    # Voice assistant setup
```

## 🏠 Add-on vs Custom Component

### Add-on (Recommended)
- Docker container
- Wyoming protocol server
- Easy install from add-on store
- Self-contained

### Custom Component (Advanced)
- Native HA integration
- Better performance
- More complex to develop/maintain

**Sinu projekti jaoks**: Add-on on piisav!

## 📦 Add-on Structure

### config.yaml
```yaml
name: "Kratt - Estonian Wake Word"
version: "1.0.0"
slug: "kratt_wake_word"
description: "First Estonian wake word detection for Home Assistant"
arch:
  - aarch64  # Raspberry Pi 4/5
  - amd64    # x86_64
url: "https://github.com/yourusername/kratt"
startup: services
boot: auto
ports:
  10400/tcp: 10400
options:
  model: "kratt"
  threshold: 0.5
  debug: false
schema:
  model: str
  threshold: float(0.0,1.0)
  debug: bool
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

# Install dependencies
RUN pip install openwakeword wyoming

# Copy wake word model
COPY rootfs/data/kratt.onnx /data/

# Copy entry script
COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
```

### run.sh
```bash
#!/usr/bin/with-contenv bashio

# Get options from config
MODEL=$(bashio::config 'model')
THRESHOLD=$(bashio::config 'threshold')
DEBUG=$(bashio::config 'debug')

bashio::log.info "Starting Kratt wake word detection..."

# Run Wyoming server
python3 -m wyoming_openwakeword \
    --uri tcp://0.0.0.0:10400 \
    --custom-model-dir /data \
    --wake-word "$MODEL" \
    --threshold "$THRESHOLD"
```

## 🔗 Voice Pipeline Configuration

Users add this to their `configuration.yaml`:

```yaml
# Wyoming Integration
wyoming:
  - platform: wake_word
    name: "Kratt"
    uri: "tcp://localhost:10400"

# Voice Assistant
assist_pipeline:
  - name: "Estonian Kratt Assistant"
    language: et
    wake_word_entity: wake_word.kratt
    stt_engine: wyoming_stt.kiirkirjutaja_int8
    stt_language: et
    conversation_engine: conversation.home_assistant
    tts_engine: tts.piper
    tts_language: et-EE
```

## 📊 Add-on Store Submission

### Requirements
1. **GitHub repo** with add-on structure
2. **README.md** with:
   - Description
   - Installation instructions
   - Configuration options
   - Screenshots
3. **Changelog** - version history
4. **Support** forum link
5. **License** (MIT recommended)

### Submission Process
1. Create add-on repo: `https://github.com/yourusername/ha-kratt-addon`
2. Test locally: `ha addons install --repository /path/to/repo`
3. Submit PR to: https://github.com/home-assistant/addons
4. Community review
5. Merged → Available in add-on store!

## 🎓 Thesis Relevance

### Chapter 4: Implementation
Document:
- Add-on architecture
- Wyoming protocol integration
- Configuration options
- Installation process

### Chapter 5: Evaluation
Measure:
- Installation success rate
- Configuration ease
- User satisfaction with integration

### Appendix
- Full configuration examples
- Troubleshooting guide
- Add-on submission process

## 🚀 Development Workflow

### Local Testing
```bash
# Build add-on locally
cd ~/kratt/home-assistant/addon
docker build -t local/kratt-addon .

# Run manually
docker run -p 10400:10400 local/kratt-addon

# Test with HA
# Settings → Add-ons → Add-on Store → ... → Repositories
# Add: http://192.168.1.100/repo
```

### Publishing
```bash
# Tag version
git tag v1.0.0
git push origin v1.0.0

# Automated build via GitHub Actions
# Users can install: Settings → Add-ons → Add-on Store → Kratt
```

## 📝 Documentation für Users

### README.md Template
```markdown
# Kratt - Estonian Wake Word for Home Assistant

First Estonian wake word detection add-on!

## Installation

1. Add repository: Settings → Add-ons → Add-on Store → ... → Repositories
2. Add URL: `https://github.com/yourusername/ha-kratt-addon`
3. Install "Kratt Wake Word"
4. Start add-on
5. Configure voice pipeline (see below)

## Configuration

```yaml
model: kratt
threshold: 0.5  # Lower = more sensitive
debug: false
```

## Voice Pipeline

Add to `configuration.yaml`:
[configuration example here]

## Support

Forum: https://community.home-assistant.io/...
Issues: https://github.com/yourusername/ha-kratt-addon/issues
```

## ⚠️ Common Issues

### Add-on won't start
- Check logs: Add-ons → Kratt → Log
- Verify port 10400 is free
- Check model file exists

### HA doesn't detect wake word
- Verify Wyoming integration is configured
- Check voice pipeline settings
- Test with: Developer Tools → Voice Assistant → Test

### False positives
- Increase threshold in add-on config
- Retrain model with more negative samples

---

**Goal**: Make it so easy that anyone can use "Kratt" in their HA setup!
