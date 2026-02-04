# Neurokõne TTS - Access Options

API test näitas, et Neurokõne API ei ole avalikult kättesaadav. Meil on 3 head varianti:

## ✅ Option A: Küsi Tanelilt API Access (SOOVITAN!)

**Miks see on parim:**
- Sa teed bakalaureusetööd Taneliga
- TartuNLP on TalTech'i partner
- Nad peaksid andma sulle access uurimistöö jaoks

**Action:**
```
Subject: Neurokõne API Access for Bachelor's Thesis

Tere Tanel,

Olen alustanud bakalaureusetööga esimese eestikeelse wake word mudeli
"Kratt" loomiseks. Plaanin kasutada synthetic data generation'it
training data laiendamiseks.

Kas oleks võimalik saada access Neurokõne API-le, et genereerida
treenimiseks vajalikud audio näited?

Alternatiivselt, kas soovitad muud lähenemist?

Aitäh!
Mattias
```

## ✅ Option B: Self-Host Neurokõne (Docker)

**Kui Tanel ei saa API access'i anda, võid ise hostida:**

```bash
# 1. Clone repo
cd ~/kratt/external-repos
git clone https://github.com/TartuNLP/text-to-speech-api
cd text-to-speech-api

# 2. Download models
# (Check releases: https://github.com/TartuNLP/text-to-speech-worker/releases)
mkdir -p models
# Download model files to models/

# 3. Run with Docker
docker-compose up -d

# 4. API available at localhost:8000
curl -X POST http://localhost:8000/v2 \
  -H "Content-Type: application/json" \
  -d '{"text":"Kratt","speaker":"mari","speed":1}'
```

**Requirements:**
- Docker Desktop
- ~2GB disk space (models)
- Runs locally on Mac/Pi

## ✅ Option C: Web Interface + Automation

**Kui API ei ole võimalik:**

```python
# Use Selenium to automate web interface
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://neurokone.ee")

phrases = ["Kratt", "Kuule Kratt", ...]
for phrase in phrases:
    # Enter text
    # Select speaker
    # Click generate
    # Download audio
    # ...
```

**Pros:**
- No API access needed
- Works immediately

**Cons:**
- Slower
- Less elegant
- Requires browser automation

## ✅ Option D: Hybrid Approach (PRAKTILINE!)

**Kui Neurokõne ei tööta kiiresti:**

1. **Start with your own voice** (50-100 samples)
   - Kõige kiirem
   - Kohe alustada saad
   - Authentic baseline

2. **Use eSpeak NG** (synthetic baseline)
   ```bash
   # eSpeak NG on command-line TTS
   brew install espeak-ng

   espeak-ng -v et "Kratt" -w kratt_espeak.wav
   ```
   - Works offline
   - Free and open
   - Not neural (lower quality) but OK for testing

3. **Add Neurokõne later** (when access available)
   - Boost dataset
   - Compare quality

## 📊 Recommended Strategy

```
Week 1 (NOW):
  1. Email Tanel about API access
  2. Meanwhile: Record own voice (50-100 samples)
  3. Test eSpeak NG as backup

Week 2:
  IF Neurokõne access granted:
    ✅ Generate 1000-3000 synthetic samples
  ELSE:
    ✅ Continue with own voice + eSpeak
    ✅ Or self-host Neurokõne locally

Week 3:
  ✅ Train initial model
  ✅ Evaluate performance
```

## 💡 Thesis Perspective

**This is actually GOOD for thesis!**

Saad kirjutada:
```
Chapter 3.2.3: Data Source Challenges

Initial attempts to access Neurokõne API revealed access
restrictions for public use. This led to exploring alternative
approaches:

A) Self-hosted deployment (demonstrates technical versatility)
B) Collaboration with TartuNLP (demonstrates research networking)
C) Hybrid approach with multiple TTS sources (demonstrates
   practical problem-solving)

This challenge actually enriched the methodology by forcing
evaluation of multiple data generation strategies.
```

**Järeldus**: Probleemid on lõputöös HÄSTI narratiiv, mitte negatiivne! 📈

---

## 🚀 Immediate Action

**RIGHT NOW:**
```bash
# Test eSpeak NG (5 min install + test)
brew install espeak-ng
espeak-ng -v et "Kratt" -w /tmp/test_espeak.wav
open /tmp/test_espeak.wav  # Listen to quality
```

**TODAY:**
- Email Tanel
- Record 10 test samples (oma hääl)
- Test eSpeak NG quality

**THIS WEEK:**
- Wait for Tanel response
- Meanwhile: Collect own voice data (50-100 samples)
- Prepare training pipeline

**Result**: Sa ei jää seisma! Progress continues either way. 🎯
