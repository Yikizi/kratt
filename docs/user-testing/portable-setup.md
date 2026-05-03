# Kaasaskantav demo setup

**Eesmärk**: Täielikult autonoomne eestikeelne voice assistant demo, mis töötab offline ja mahub seljakotti.

## Arhitektuur

```
[iPhone] ──USB tether──▶ [MacBook Pro M1 Pro 32GB]
                              ├── macOS Internet Sharing (WiFi AP)
                              ├── Docker
                              │   ├── Home Assistant
                              │   ├── Kiirkirjutaja STT (~3GB)
                              │   └── Piper TTS
                              ├── Ollama
                              │   └── Gemma 3 12B (~8GB)
                              └── Logging/telemetria
                                  ▲ WiFi (AP)
                         ┌────────┴────────┐
                   [ESP32 + mic]      [WiFi pirn]
                   wake word          kontrollitav seade
                   satellite
```

## RAM kalkulatsioon

| Komponent | RAM |
|-----------|-----|
| macOS + Desktop | ~4GB |
| Home Assistant (Docker) | ~1GB |
| Kiirkirjutaja STT (Docker) | ~3GB |
| Ollama Gemma 3 12B | ~8GB |
| Piper TTS | ~0.5GB |
| Varu | ~15.5GB |
| **Kokku** | **~32GB** |

Tihe, aga mahub. Kui RAM lõppeb, kaaluda väiksemat LLM mudelit (8B → ~5GB).

## Pakkimise checklist

### Hardware
- [ ] MacBook Pro + laadija
- [ ] iPhone + USB-C kaabel (tethering)
- [ ] ESP32 + mikrofon + USB kaabel (toide)
- [ ] WiFi pirn + pirni adapter (kui lamp pole kohal)
- [ ] Laualamp (pirni jaoks) — või kasutada kohapealset
- [ ] Pikendusjuhe (igaks juhuks)

### Software (ette valmistada)
- [ ] Docker images pulled: HA, Kiirkirjutaja, Piper
- [ ] Ollama mudel alla laetud (Gemma 3 12B)
- [ ] macOS Internet Sharing konfigureeritud ja testitud
- [ ] ESP32/active demo path configured with the frozen active model (pilot default: `v16c`) and threshold
- [ ] WiFi pirn seadistatud HA-s (testitud kodus enne)
- [ ] Google Forms küsimustik loodud + QR-kood prinditud
- [ ] `kratt user-test` recorder tested (dry-run + real mic)
- [ ] Logging/replay scripts tested

### Enne üritust testida
- [ ] Kogu stack üles: AP → ESP32 ühendub → wake word → STT → LLM → pirn
- [ ] E2E latency mõõta (peaks olema <3s)
- [ ] False positive test: räägi 2 minutit ilma wake wordita
- [ ] Aku kestvus: MacBook peaks vastu pidama ~3h (20 osalejat)
- [ ] iPhone tethering stabiilsus

## Võrgu konfigutratsioon

### macOS Internet Sharing
1. System Settings → General → Sharing → Internet Sharing
2. Share from: iPhone USB (kui ühendatud) või Ethernet
3. To: Wi-Fi
4. WiFi Options: Network name: `kratt-demo`, WPA3, parool

### Staatiline IP plaan
| Seade | IP |
|-------|----|
| MacBook (AP) | 192.168.2.1 |
| ESP32 | DHCP → 192.168.2.x |
| WiFi pirn | DHCP → 192.168.2.x |

## Startup järjekord

```bash
# 1. Lülita Internet Sharing sisse (GUI-st)
# 2. Käivita Docker stack
docker compose -f docker/demo-compose.yml up -d

# 3. Käivita Ollama
ollama serve &
ollama run gemma3:12b  # preload

# 4. Lülita ESP32 sisse (USB)
# 5. Lülita pirn sisse
# 6. Testi: "Kuule Kratt, lülita tuli põlema"
```

## Fallback plaanid

| Probleem | Lahendus |
|----------|----------|
| WiFi pirn ei ühendu AP-ga | Kasuta pirni enda AP/pairing mode'i |
| Ollama liiga aeglane | Kasuta väiksemat mudelit (8B) või HA intent matching |
| MacBook aku saab otsa | Laadija, või testi väiksema grupiga |
| ESP32 ei ühendu | Flashitud backup SSID, või USB serial debug |
| STT ei tööta | Restart Kiirkirjutaja container |
