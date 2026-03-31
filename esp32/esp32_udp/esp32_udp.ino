/*
 * ESP32 Audio - UDP传输
 *
 * 硬件接线 (参考 docs/hardware/pinout.md):
 *   ESP32 GPIO0  → INMP441 SCK (I2S时钟)
 *   ESP32 GPIO1  → INMP441 WS  (字选择)
 *   ESP32 GPIO2  → INMP441 SD  (串行数据)
 *   ESP32 3V3    → INMP441 VDD
 *   ESP32 GND    → INMP441 GND 和 L/R
 */

#include <Arduino.h>
#include <WiFi.h>
#include <driver/i2s.h>
#include <WiFiUdp.h>

// ============ 配置 ============
// WiFi设置 - 请修改为你的WiFi
#define WIFI_SSID      "你的WiFi名称"
#define WIFI_PASSWORD  "你的WiFi密码"

// I2S引脚配置 (ESP32-S3)
#define I2S_SCK_PIN    GPIO_NUM_0   // I2S时钟
#define I2S_WS_PIN     GPIO_NUM_1   // 字选择
#define I2S_SD_PIN     GPIO_NUM_2   // 串行数据

// 音频配置
#define SAMPLE_RATE     16000       // 采样率 16kHz
#define FRAME_SIZE      512         // 帧大小
#define UDP_PORT        8888         // UDP端口

bool isStreaming = false;
uint32_t frameCnt = 0;
int16_t audioBuf[FRAME_SIZE];
WiFiUDP udp;

void initI2S() {
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
  };
  i2s_pin_config_t pin = {
    .bck_io_num = I2S_SCK_PIN,
    .ws_io_num = I2S_WS_PIN,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD_PIN,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== ESP32 UDP Audio ===");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int timeout = 30;
  while (WiFi.status() != WL_CONNECTED && timeout > 0) {
    delay(500); Serial.print("."); timeout--;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\nWiFi OK: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("UDP Port: %d\n", UDP_PORT);
  } else {
    Serial.println("\nWiFi Failed!"); while(1) delay(1000);
  }

  initI2S();
  Serial.println("=== Ready ===");
  Serial.println("Send 'start' to begin streaming");
}

void loop() {
  // 处理串口命令
  if(Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if(cmd == "start") {
      isStreaming = true;
      frameCnt = 0;
      Serial.println("Streaming started");
    }
    else if(cmd == "stop") {
      isStreaming = false;
      Serial.printf("Stopped: %lu frames\n", frameCnt);
    }
  }

  // 录制并发送UDP
  if(isStreaming) {
    size_t bytesRead = 0;
    i2s_read(I2S_NUM_0, audioBuf, sizeof(audioBuf), &bytesRead, 0);

    if(bytesRead > 0) {
      // 发送到广播地址
      udp.beginPacket("255.255.255.255", UDP_PORT);
      udp.write((uint8_t*)audioBuf, bytesRead);
      udp.endPacket();
      frameCnt++;

      if(frameCnt % 50 == 0) {
        Serial.printf("Sent: %lu frames\n", frameCnt);
      }
    }
  }

  delay(5);
}