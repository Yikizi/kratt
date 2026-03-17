# Korvo-2 v3.1 Recorder — Debugging Log

**Date**: 2026-03-16 to 2026-03-17
**Board**: ESP32-S3-Korvo-2 v3.1
**Firmware**: ESP-IDF v5.5.3 + esp_codec_dev ^1.3.4

## Problem

Recordings from the ES7210 microphone array sounded high-pitched ("chipmunk effect"). Audio was unintelligible at the configured 48kHz sample rate. Playing back at 32kHz sounded closest to natural speech, suggesting the effective sample rate was wrong.

## Root Cause (3 issues)

### 1. Wrong bit width: 16-bit instead of 32-bit

**Symptom**: Garbled audio, wrong sample boundaries.

The Korvo-2 v3.1 `board_def.h` specifies:
```c
#define CODEC_ADC_BITS_PER_SAMPLE  ((i2s_data_bit_width_t)32)
```

The ES7210 is a 24-bit ADC. It outputs samples left-justified in 32-bit TDM slots: `0xXXXXXX00` (24 data bits + 8 zero-padding bits). Our code configured I2S for 16-bit, causing every sample to straddle two int16_t positions and corrupting the deinterleaving.

**Fix**: `I2S_DATA_BIT_WIDTH_16BIT` → `I2S_DATA_BIT_WIDTH_32BIT`, buffer type `int16_t` → `int32_t`, and downconvert with `>> 16` to get the top 16 bits of the 24-bit value.

### 2. Wrong TDM slot mapping

**Symptom**: All mic files contained silence (reading from empty slots).

We assumed the "RMNM" channel format from `board_def.h`:
```
Slot 0 = R (AEC reference)    → we read MIC1 here
Slot 1 = M (MIC1)             → we read MIC2 here
Slot 2 = N (null)
Slot 3 = M (MIC2)
```

But "RMNM" only applies when **MIC1+MIC2+MIC3** are all enabled. MIC3 is not a physical microphone — it's a loopback from the ES8311 speaker DAC output, used for Acoustic Echo Cancellation (AEC). Since we only enabled MIC1+MIC2, the ES7210 maps its ADC pairs differently:

```
ADC pair 1: MIC1 → slot 0, MIC2 → slot 2
ADC pair 2: (disabled) → slots 1, 3 empty
```

**Verified** by adding a debug hex dump of the first I2S DMA buffer read:
```
[0] slot0 = 0x011ECD00  ← MIC1 data (24-bit left-justified)
[1] slot1 = 0x00000000  ← empty
[2] slot2 = 0x01366600  ← MIC2 data
[3] slot3 = 0x00000000  ← empty
```

**Fix**: `MIC1_SLOT=0`, `MIC2_SLOT=2` (not 1 and 3).

### 3. channel_mask caused BCLK miscalculation → halved sample rate

**Symptom**: Chipmunk audio. WAV header said 48kHz but effective sample rate was 24kHz.

**Evidence**: A 24-second recording produced 1,152,000 bytes per mic.
- 1,152,000 / 2 bytes = 576,000 samples
- 576,000 / 24 sec = **24,000 Hz** (exactly half of 48kHz)

Confirmed by re-interpreting the WAV at 24kHz with ffmpeg — audio sounded perfectly natural.

**Root cause**: `esp_codec_dev_open()` reconfigures the I2S channel using the `channel_mask` parameter. It counts the set bits in the mask to compute BCLK:

```
channel_mask = ES7210_SEL_MIC1 | ES7210_SEL_MIC2 = 0x03 → 2 bits set
BCLK = 48000 × 2 × 32 = 3,072,000 Hz
TDM frame = 4 slots × 32 bits = 128 bits
WS = 3,072,000 / 128 = 24,000 Hz  ← WRONG!
```

The correct calculation needs all 4 TDM slots:
```
channel_mask = 0x000F → 4 bits set
BCLK = 48000 × 4 × 32 = 6,144,000 Hz
WS = 6,144,000 / 128 = 48,000 Hz  ← CORRECT
```

**Fix**: `channel_mask = 0x000F` (all 4 TDM slots), not just the 2 active mics.

**Note**: This is arguably a design issue in `esp_codec_dev` / I2S_IF — the BCLK should be computed from the total TDM slot count, not the number of "useful" channels. The wire timing must accommodate all slots regardless of which carry data.

## Additional fix: MCLK multiple

The driver logged:
```
W (378) i2s_tdm: the current mclk multiple is too small, adjust the mclk multiple to 384
```

With 32-bit TDM, `I2S_MCLK_MULTIPLE_256` gives MCLK/BCLK = 2, which is insufficient. The driver auto-adjusted to 384 (ratio = 3), but the ES7210 codec config (`mclk_div`) still said 256, creating a mismatch.

**Fix**: Set both to `I2S_MCLK_MULTIPLE_384` explicitly.

## Hardware notes: Korvo-2 v3.1 microphone setup

| ES7210 Input | Connected to | Purpose |
|---|---|---|
| MIC1 | Left MEMS microphone (physical) | Voice capture |
| MIC2 | Right MEMS microphone (physical) | Voice capture |
| MIC3 | ES8311 DAC output (loopback) | AEC echo reference |
| MIC4 | Not connected | — |

- The board has **2 physical microphones**, not 3
- MIC3 is for Acoustic Echo Cancellation: the ES7210 captures what the speaker outputs, so the Audio Front-End (AFE) can subtract it from the mic signal
- Without a speaker connected, MIC3 is useless for our recording purposes
- The `board_def.h` channel format `"RMNM"` (Reference, Mic, Null, Mic) reflects the AFE's view when all 3 inputs are active

## Debugging methodology

1. **Symptom analysis**: Tested playback at different sample rates (16k, 24k, 32k, 48k) to estimate the pitch shift factor
2. **Literature search**: Found GitHub issue espressif/esp-idf#10630 describing alternating zero samples in TDM 16-bit mode — pointed to slot_bit_width mismatch
3. **Board documentation**: Fetched `board_def.h` from esp-adf repo, discovered 32-bit ADC config, "RMNM" channel format, and that MIC3 is AEC (not a physical mic)
4. **DMA buffer hex dump**: Added debug print of first 8 int32_t values after I2S read — immediately revealed which slots contained data and which were empty
5. **Data rate calculation**: Compared recording duration with file size to compute effective sample rate — showed exactly 24kHz, confirming clock miscalculation
6. **ffmpeg re-interpretation**: Used `asetrate=24000` to confirm audio content was correct, just at wrong rate

## Lessons learned

1. **Always check the board definition file** (`board_def.h`) — it specifies the intended bit width, sample rate, channel format, and pin mapping for the specific board revision
2. **Debug prints of raw DMA data are invaluable** — one hex dump immediately showed slot mapping and data format, saving hours of guesswork
3. **`esp_codec_dev` reconfigures I2S behind your back** — calling `esp_codec_dev_open()` re-initializes the I2S channel. Parameters like `channel_mask` directly affect clock generation, not just data routing
4. **TDM slot count ≠ active channel count** — the wire timing (BCLK) must be computed for ALL slots, even empty ones. Only 2 active channels doesn't mean the clock can run at half speed
5. **Compute expected vs actual data rates** — a simple division (bytes / duration) immediately quantified the problem as exactly 2× speed
6. **ES7210 ADC pair mapping is not sequential** — with only MIC1+MIC2 enabled, they map to slots 0,2 (even positions), not 0,1. This follows the ES7210's internal ADC pair architecture
7. **MIC3 on Korvo-2 is not a microphone** — it's an AEC reference input. Don't enable it unless doing echo cancellation
