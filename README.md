# ESP32 Audio AI

ESP32 + MEMS麦克风 + AI语音分析的完整开源项目。(multiagent项目数据收集前置工作)

## 系统架构

```
┌─────────────┐     WiFi UDP     ┌─────────────┐     音频文件     ┌─────────────┐
│  ESP32S3   │ ───────────────► │     PC      │ ───────────────► │  AI分析器   │
│ + INMP441  │   (广播音频)       │  (录音保存)  │                   │ (Whisper)   │
│  麦克风采集  │                   │  client_udp │                   │  语音转文字  │
└─────────────┘                   └─────────────┘                   └─────────────┘
```

## 功能特点

- **ESP32音频采集**: I2S接口 + INMP441 MEMS麦克风
- **WiFi实时传输**: UDP广播，16kHz采样率
- **语音识别**: Whisper本地模型或API
- **停顿检测**: WebRTC VAD
- **关键词提取**: jieba中文分词
- **语速统计**: 字/分钟计算

## 目录结构

```
esp32-audio-ai/
├── README.md              # 本文件
├── LICENSE               # MIT许可证
├── SPEC.md               # 项目规格说明
├── docs/                 # 硬件文档
│   └── hardware/
│       └── pinout.md     # 引脚接线图
├── esp32/                # ESP32固件
│   └── esp32_udp/
│       └── esp32_udp.ino # Arduino UDP版本
├── pc/                   # PC客户端
│   ├── client_udp.py    # UDP录音客户端
│   └── requirements.txt
└── ai_speech_analysis/   # AI分析工具
    ├── analyze.py        # 主分析脚本
    ├── requirements.txt
    ├── .env.example
    └── output/           # 分析结果输出
```

## 快速开始

### 1. 硬件准备

- ESP32-S3 开发板
- INMP441 MEMS麦克风模块
- 连接线

接线参考: [docs/hardware/pinout.md](docs/hardware/pinout.md)

| ESP32 GPIO | INMP441 | 功能 |
|-----------|---------|------|
| GPIO0 | SCK | I2S时钟 |
| GPIO1 | WS | 字选择 |
| GPIO2 | SD | 串行数据 |
| 3V3 | VDD | 3.3V电源 |
| GND | GND | 地 |

### 2. ESP32固件

1. 用Arduino IDE打开 `esp32/esp32_udp/esp32_udp.ino`
2. 修改WiFi配置:
   ```cpp
   const char* ssid = "你的WiFi名称";
   const char* password = "你的WiFi密码";
   ```
3. 上传到ESP32

### 3. PC录音客户端

```bash
cd pc
pip install -r requirements.txt

# 录音30秒
python client_udp.py --duration 30 --save audio.wav
```

### 4. AI语音分析

```bash
cd ai_speech_analysis
pip install -r requirements.txt

# 复制配置
cp .env.example .env
# 编辑.env填入API Key或设置USE_LOCAL_MODEL=true

# 运行分析
python analyze.py audio.wav

# 使用本地模型(免费)
python analyze.py audio.wav --local --model base
```

## 使用示例

```bash
# 1. ESP32发送音频
# 在Arduino串口监视器输入: start

# 2. PC录制
python pc/client_udp.py --duration 60 --save my_audio.wav

# 3. AI分析
python ai_speech_analysis/analyze.py my_audio.wav -o result.json
```

## 输出示例

```json
{
  "file": "my_audio.wav",
  "duration": 30.5,
  "text": "今天天气很好，我们去公园玩吧",
  "speed": 114,
  "speech_ratio": 0.85,
  "pause_count": 3,
  "keywords": ["天气", "公园"],
  "segments": [
    {"type": "speech", "start": 0.0, "end": 2.5, "duration": 2.5},
    {"type": "silence", "start": 2.5, "end": 3.0, "duration": 0.5}
  ]
}
```

## 配置说明

### ESP32 WiFi配置

在 `esp32/esp32_udp/esp32_udp.ino` 中修改:

```cpp
const char* ssid = "你的WiFi";      // WiFi名称
const char* password = "你的密码";   // WiFi密码
#define UDP_PORT 8888               // UDP端口
```

### AI分析配置

复制 `.env.example` 为 `.env`:

```bash
# OpenAI API (可选)
OPENAI_API_KEY=sk-...

# 使用本地模型 (推荐，免费)
USE_LOCAL_MODEL=true
MODEL_SIZE=base  # tiny, base, small, medium, large
```

## 技术规格

| 参数 | 值 |
|------|-----|
| 采样率 | 16kHz |
| 位深 | 16bit |
| 通道 | 单声道 |
| 传输协议 | UDP广播 |
| ESP32时钟 | 240MHz |

## 依赖

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

## License

MIT License - see [LICENSE](LICENSE)

## 参考资料

- [ESP32-S3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [INMP441 Datasheet](https://www.invensense.com/download-pdf/?pdf_path=INMP441.pdf)
- [Whisper](https://github.com/openai/whisper)
