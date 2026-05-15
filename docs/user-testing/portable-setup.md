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
- [ ] macOS Internet Sharing seadistatud ja testitud
- [x] ESPHome local model copy prepared for pilot default `v16c` at cutoff `0.996` (`kratt prepare-esphome-model v16c --cutoff 0.996`; enne ESP32 demo tuleb veel püsivara koostada ja seadme välkmällu kirjutada)
- [ ] WiFi pirn seadistatud HA-s (testitud kodus enne)
- [ ] Google Forms küsimustik loodud + QR-kood prinditud
- [ ] `kratt user-test` recorder tested (dry-run + real mic)
- [ ] Recorder input device chosen with `kratt user-test --list-devices`; run a short real-mic check and reject any device that gives near-zero RMS warnings
- [x] Synthetic fixture recorder/validator/replay path tested (`kratt user-test-fixtures` → `kratt user-test --audio-fixture-dir` → `kratt replay-user-test`)
- [ ] Real-mic replay scripts tested

### Enne üritust testida
- [ ] Kogu stack üles: AP → ESP32 ühendub → wake word → STT → LLM → pirn
- [ ] E2E latency mõõta (peaks olema <3s)
- [ ] False positive test: räägi 2 minutit ilma wake wordita
- [ ] Aku kestvus: MacBook peaks vastu pidama ~1,5–2h (kuni 10 osalejat)
- [ ] iPhone tethering stabiilsus

## Võrguseadistus

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

### Valikuline BLE → WiZ sild

Kasuta seda ainult fallback'ina, kui MacBook ei saa pirniga samasse võrku või kui ESP32 peab olema pirni-poolse AP osana. Tavaline tee jääb `kratt demo --wiz`. Vaata detailsemat seadistuse ja testimise juhist [hardware/esp32/firmware/recorder/BLE_BRIDGE.md](../../hardware/esp32/firmware/recorder/BLE_BRIDGE.md).

```bash
./cli/kratt ble-wiz --on
./cli/kratt demo --wiz --ble-bridge --no-wakeword
```

Oodatav BLE identiteet: `Kratt-BLE-Bridge`, service UUID `c6d6f8f5-6b2d-6d4b-8f5d-0f1d2c3b4a50`.

## Recorder sanity check

```bash
./cli/kratt user-test-fixtures --output-dir output/user-test-fixtures/ten-minute-v1
./cli/kratt user-test SYNTH01 --audio-fixture-dir output/user-test-fixtures/ten-minute-v1 --auto-advance --new-session-subdir
./cli/kratt user-test --list-devices
./cli/kratt user-test TEST_REAL --new-session-subdir --device <input_device_id>
./cli/kratt validate-user-test output/user-tests/TEST_REAL/<session_dir> --fail-on-warnings
./cli/kratt replay-user-test output/user-tests/TEST_REAL/<session_dir>
./cli/kratt summarize-user-test output/user-test-replay
```

`kratt summarize-user-test` excludes dry-run/synthetic fixture rows by default; use `--include-smoke` only for debug.

Local 2026-05-04 smoke result: CoreAudio device selection was unstable and some listed/default inputs produced zero RMS or PortAudio channel errors in this harness. Always run the smoke test and pick a device that returns non-zero RMS before recording participants; re-check device IDs before every test day because macOS device numbering can change.

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
