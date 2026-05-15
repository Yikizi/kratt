# Korvo-2 serial PCM streamer

Tiny ESP-IDF firmware for using the ESP32-S3-Korvo-2 microphone path as the
input device for the Python demo pipeline.

It captures the two physical ES7210 microphones as 16 kHz 16-bit stereo
PCM and writes framed binary packets over UART0/USB serial. The host demo
selects `mic1`, `mic2`, or `mix`.

Host pipeline:

```bash
./cli/kratt korvo-streamer --flash --port /dev/cu.usbserial-2130
./cli/kratt demo --audio-source korvo-serial --serial-port /dev/cu.usbserial-2130
```

Frame format, little-endian:

```c
struct {
  char magic[4];        // "KPCM"
  uint16_t version;     // 1
  uint16_t header_size; // 24
  uint32_t seq;
  uint32_t sample_rate; // 16000
  uint32_t payload_bytes;
  uint16_t channels;    // 2 for current firmware
  uint16_t bits;        // 16
  int16_t pcm[payload_bytes / 2]; // interleaved mic1, mic2
};
```

The host reader scans for `KPCM`, so ESP boot logs before app startup are safe.
