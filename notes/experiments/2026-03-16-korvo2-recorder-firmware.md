# ESP32-S3 Korvo-2 — Custom C Recorder Firmware

Date: 2026-03-16 to 2026-03-17

## Goal

Build a standalone recording device using the Korvo-2 v3.1 for collecting Estonian wake word ("Kratt") training data. Record from both physical microphones simultaneously into separate mono WAV files on an SD card, controlled by hardware buttons.

## Technology Choice: ESP-IDF C (not C++, not ESPHome)

- Previous ESPHome YAML approach worked for voice satellite demo but doesn't support custom recording logic
- Chose C over C++ because we exclusively use C libraries (ESP-IDF, esp_codec_dev) — wrapping C APIs in C++ adds no value and complicates the thesis justification
- ESP-IDF v5.5.3 gives direct hardware control needed for TDM deinterleaving and WAV file writing
- Bachelor's thesis requires all technology choices to be explicitly justified

## Hardware

- Board: ESP32-S3-Korvo-2 v3.1 (Espressif)
- Microphones: 2× physical MEMS mics connected to ES7210 4-channel ADC
- SD card: 128GB microSD, FAT32 formatted, label "KRATT"
- Buttons: 6 mechanical buttons on GPIO5 via ADC resistor ladder

### Key discovery: MIC3 is not a microphone

The ES7210 has 4 ADC inputs, but on Korvo-2:
- MIC1, MIC2 = physical MEMS microphones (left, right)
- MIC3 = loopback from ES8311 speaker DAC (for AEC echo cancellation)
- MIC4 = not connected

Source: `board_def.h` channel format `"RMNM"` (Reference, Mic, Null, Mic) and Espressif documentation.

## Development Process

### Step 1: Test projects (individually validated each peripheral)

Built 4 separate ESP-IDF projects before combining:
1. **logger** — ADC button value logger. Empirically mapped all 6 buttons' ADC values via resistor ladder on GPIO5
2. **mic-test** — ES7210 RMS level monitor. Confirmed I2S TDM + I2C codec init works, all 3 mic channels show signal
3. **speaker-test** — ES8311 DAC test. Speaker JST connector is empty on our board, deferred
4. **sd-test** (inline in recorder) — SDMMC 1-bit mode + VFS FAT. Confirmed file write/read

### Step 2: Combined recorder firmware

Merged all working peripherals into one `app_main()`:
- SD card init → I2S TDM init → ES7210 codec init → ADC button init
- Main loop: poll buttons (edge detection), on REC start recording, on MUTE stop
- Recording: read I2S DMA buffer → deinterleave TDM slots → write per-mic WAV files
- WAV header with placeholder size, updated with fseek on stop

### Step 3: Debug audio quality (the hard part)

See `DEBUGGING.md` for full details. Three cascading issues:

1. **16-bit vs 32-bit**: board uses 32-bit TDM slots (ES7210 is 24-bit ADC, left-justified in 32-bit)
2. **Wrong slot mapping**: with MIC1+MIC2 only, ES7210 maps to slots 0,2 (not 0,1 as assumed). Verified via hex dump of DMA buffer
3. **BCLK halved**: `esp_codec_dev_open()` computed bit clock from `channel_mask` bit count (2 mics = 2 channels = half the BCLK needed for 4-slot TDM). Effective sample rate was 24kHz instead of 48kHz. Fix: set `channel_mask=0x000F` for all 4 TDM slots

## Technical Details

### Button ADC values (resistor ladder on GPIO5)

| Button | ADC value | Range used |
|--------|-----------|------------|
| REC | ~2805 | 2650-2950 |
| MUTE | ~2285 | 2100-2400 |
| SET | ~1895 | (not used) |
| PLAY | ~1254 | (not used) |
| VOL- | ~905 | (not used) |
| VOL+ | ~397 | (not used) |
| None | ~4095 | >4000 |

### I2S TDM Configuration (final, working)

```c
I2S_DATA_BIT_WIDTH_32BIT        // ES7210 outputs 24-bit left-justified in 32-bit
I2S_SLOT_MODE_STEREO            // multi-channel (not mono duplication)
I2S_TDM_SLOT0|SLOT1|SLOT2|SLOT3 // all 4 TDM slots active
MCLK_MULTIPLE_384               // 32-bit TDM needs MCLK/BCLK ≥ 3
SAMPLE_RATE = 48000
```

### ES7210 TDM slot mapping (MIC1+MIC2 only)

```
Slot 0 = MIC1 (left mic)    ← ADC pair 1, even
Slot 1 = empty               ← ADC pair 2, even (disabled)
Slot 2 = MIC2 (right mic)   ← ADC pair 1, odd
Slot 3 = empty               ← ADC pair 2, odd (disabled)
```

### WAV output format

- Mono, 16-bit PCM, 48kHz per mic
- 32-bit I2S data downconverted to 16-bit via `>> 16` (top 16 of 24 bits)
- Files: `rec_NNNN_mic1.wav`, `rec_NNNN_mic2.wav`
- Auto-incrementing recording number by scanning existing files on SD card

## Fixes Applied During Development

| Issue | Cause | Fix |
|-------|-------|-----|
| CMakeLists typo | `project.make` → `project.cmake` | Manual fix |
| Missing `esp_check.h` | `ESP_RETURN_ON_ERROR` needs it | Added include |
| Stack overflow on boot | codec init deep call stack | `CONFIG_ESP_MAIN_TASK_STACK_SIZE=8192` |
| Double I2S enable | `esp_codec_dev_open()` enables internally | Removed explicit `i2s_channel_enable()` |
| fopen "invalid argument" | FAT 8.3 filename limit | `CONFIG_FATFS_LFN_HEAP=y` |
| SD mount failure | Card had RPi OS partitions | Reformatted as FAT32 |
| Button double-trigger | Polling too fast (20ms) | Edge detection (press on transition only) |
| High-pitched audio | 3 cascading TDM issues | See DEBUGGING.md |

## Lessons Learned

1. **Start with isolated test projects** — validate each peripheral alone before combining. Much easier to debug
2. **Read the board definition file** — `board_def.h` contains authoritative hardware configuration that may differ from generic examples
3. **Add DMA buffer hex dumps early** — one debug print revealed slot mapping and data format instantly
4. **`esp_codec_dev` is a leaky abstraction** — it reconfigures I2S behind your back. Understand what `esp_codec_dev_open()` does to your I2S channel
5. **Calculate expected vs actual data rates** — simple arithmetic (bytes / time) immediately quantified the sample rate problem
6. **Don't assume channel mapping** — ES7210 ADC pair architecture puts MIC1,MIC2 at slots 0,2 (not 0,1) when MIC3 is disabled
7. **Resistor ladder buttons need empirical calibration** — ADC values vary with voltage divider tolerances, always measure first

## Status

- [x] Recording works (both mics, WAV files on SD card)
- [x] Audio content verified correct (24kHz re-interpretation test)
- [ ] Verify 48kHz sample rate after channel_mask fix (pending flash + test)
- [ ] Compare recording quality with iPhone reference (`~/Downloads/Kratt.m4a`)
- [ ] Add speaker/buzzer feedback for REC start/stop (needs physical speaker)
- [ ] Switch to 16kHz sample rate for wake word training (48kHz is overkill)
- [ ] Remove debug print before production use
