# Hardware Pin Mapping

## INMP441 MEMS Microphone Pinout

```
┌─────────────────┐
│  INMP441 Module  │
├─────────────────┤
│ GND  │  L/R   │ ← Connect L/R to GND for I2S slave
│ VDD   │  3V3   │ ← 3.3V from ESP32
│ GND   │  GND   │ ← Ground
│ SCK   │  SCK   │ ← I2S Clock
│ WS    │  WS    │ ← I2S Word Select
│ SD    │  SD    │ ← I2S Serial Data
└─────────────────┘
```

## ESP32-S3 Pin Assignment

### Single Microphone (MVP)
| ESP32 GPIO | INMP441 Pin | Function |
|-----------|-----------|---------|
| GPIO0 | SCK | I2S Clock |
| GPIO1 | WS | Word Select |
| GPIO2 | SD | Serial Data |
| 3V3 | VDD | 3.3V Power |
| GND | GND | Ground |
| GND | L/R | Left/Right (GND for slave) |

### 4-Microphone Array (TDM Mode)
| MIC | BCLK | WS | SD | Notes |
|-----|------|----|----|------|
| MIC 1 | GPIO0 | GPIO1 | GPIO2 | I2S0 |
| MIC 2 | GPIO3 | GPIO4 | GPIO5 | I2S1 |
| MIC 3 | GPIO6 | GPIO7 | GPIO8 | Extended |
| MIC 4 | GPIO9 | GPIO10 | GPIO11 | Extended |

## Power Connections

```
ESP32-S3 DevKit
├── USB-C (5V) → Power
├── 3V3 (500mA max) → INMP441 VDD
└── GND → INMP441 GND
```

## Quick Start Wiring

1. **Power**: Connect ESP32 3V3 to INMP441 VDD
2. **Ground**: Connect ESP32 GND to INMP441 GND and L/R
3. **I2S Clock**: ESP32 GPIO0 → INMP441 SCK
4. **Word Select**: ESP32 GPIO1 → INMP441 WS
5. **Serial Data**: ESP32 GPIO2 → INMP441 SD