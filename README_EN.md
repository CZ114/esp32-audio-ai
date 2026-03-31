# ESP32 Audio AI

An open-source ESP32 audio capture and AI speech analysis solution.

## System Architecture

```
┌─────────────┐     WiFi UDP     ┌─────────────┐     Audio File     ┌─────────────┐
│  ESP32S3   │ ───────────────► │     PC      │ ───────────────► │  AI Analyzer│
│ + INMP441  │   (Broadcast)    │  (Recording) │                   │  (Whisper)  │
│  Mic Capture│                   │  client_udp │                   │ STT + VAD   │
└─────────────┘                   └─────────────┘                   └─────────────┘
```

## Features

- **ESP32 Audio Capture**: I2S interface + INMP441 MEMS microphone
- **WiFi Real-time Transmission**: UDP broadcast, 16kHz sampling
- **Speech Recognition**: Whisper local model or API
- **Pause Detection**: WebRTC VAD
- **Keyword Extraction**: jieba Chinese word segmentation
- **Speed Calculation**: Words per minute

## Project Structure

```
esp32-audio-ai/
├── README.md              # Chinese version
├── README_EN.md          # English version
├── LICENSE               # MIT License
├── SPEC.md               # Project specification
├── docs/hardware/
│   └── pinout.md         # Pin wiring diagram
├── esp32/esp32_udp/
│   └── esp32_udp.ino     # Arduino UDP version
├── pc/
│   ├── client_udp.py     # UDP recording client
│   └── requirements.txt
└── ai_speech_analysis/   # AI analysis tools
    ├── analyze.py        # Main analysis script
    ├── requirements.txt
    ├── .env.example
    └── output/
```

## Quick Start

### 1. Hardware Setup

- ESP32-S3 development board
- INMP441 MEMS microphone module
- Jumper wires

Wiring reference: [docs/hardware/pinout.md](docs/hardware/pinout.md)

| ESP32 GPIO | INMP441 | Function |
|-----------|---------|----------|
| GPIO0 | SCK | I2S Clock |
| GPIO1 | WS | Word Select |
| GPIO2 | SD | Serial Data |
| 3V3 | VDD | 3.3V Power |
| GND | GND | Ground |

### 2. ESP32 Firmware

1. Open `esp32/esp32_udp/esp32_udp.ino` in Arduino IDE
2. Modify WiFi configuration:
   ```cpp
   #define WIFI_SSID "Your WiFi SSID"
   #define WIFI_PASSWORD "Your WiFi Password"
   ```
3. Upload to ESP32

### 3. PC Recording Client

```bash
cd pc
pip install -r requirements.txt

# Record 30 seconds
python client_udp.py --duration 30 --save audio.wav
```

### 4. AI Speech Analysis

```bash
cd ai_speech_analysis
pip install -r requirements.txt

# Copy and edit config
cp .env.example .env

# Run analysis
python analyze.py audio.wav

# Use local model (free)
python analyze.py audio.wav --local --model base
```

## Usage Example

```bash
# 1. ESP32 sends audio
# In Arduino Serial Monitor, type: start

# 2. PC records
python pc/client_udp.py --duration 60 --save my_audio.wav

# 3. AI analysis
python ai_speech_analysis/analyze.py my_audio.wav -o result.json
```

## Output Example

```json
{
  "file": "my_audio.wav",
  "duration": 30.5,
  "text": "The weather is nice today",
  "speed": 120,
  "speech_ratio": 0.85,
  "pause_count": 3,
  "keywords": ["weather", "nice"],
  "segments": [
    {"type": "speech", "start": 0.0, "end": 2.5, "duration": 2.5},
    {"type": "silence", "start": 2.5, "end": 3.0, "duration": 0.5}
  ]
}
```

## Configuration

### ESP32 WiFi

In `esp32/esp32_udp/esp32_udp.ino`:

```cpp
#define WIFI_SSID "Your WiFi"      // WiFi SSID
#define WIFI_PASSWORD "Your Password" // WiFi Password
#define UDP_PORT 8888              // UDP port
```

### AI Analysis

Copy `.env.example` to `.env`:

```bash
# OpenAI API (optional)
OPENAI_API_KEY=sk-...

# Use local model (recommended, free)
USE_LOCAL_MODEL=true
MODEL_SIZE=base  # tiny, base, small, medium, large
```

## Technical Specs

| Parameter | Value |
|-----------|-------|
| Sample Rate | 16kHz |
| Bit Depth | 16bit |
| Channels | 1 (Mono) |
| Protocol | UDP Broadcast |
| ESP32 Clock | 240MHz |

## Dependencies

### ESP32
- ESP32 Arduino Core >= 2.0
- WiFi library
- driver/i2s

### PC Client
- Python >= 3.8
- numpy

### AI Analysis
- Python >= 3.8
- openai / whisper
- webrtcvad
- jieba
- numpy, scipy

## References

- [ESP32-S3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [INMP441 Datasheet](https://www.invensense.com/download-pdf/?pdf_path=INMP441.pdf)
- [Whisper](https://github.com/openai/whisper)

## License

MIT License - see [LICENSE](LICENSE)
