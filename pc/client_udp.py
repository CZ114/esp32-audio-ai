#!/usr/bin/env python3
"""
ESP32 Audio - UDP Client (标准库)
"""

import socket
import struct
import wave
import time
import sys

UDP_PORT = 8888
SAMPLE_RATE = 16000
FRAME_SIZE = 512


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=UDP_PORT)
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--save", default="output.wav")
    args = parser.parse_args()

    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", args.port))
    sock.settimeout(0.5)

    print(f"UDP listening on port {args.port}...")

    audio_data = []
    frames = 0
    start_time = time.time()
    last_report = 0

    while time.time() - start_time < args.duration:
        try:
            data, addr = sock.recvfrom(FRAME_SIZE * 2)
            if data:
                samples = struct.unpack("<" + "h" * (len(data) // 2), data)
                audio_data.extend(samples)
                frames += 1

                elapsed = int(time.time() - start_time)
                if elapsed > last_report:
                    print(f"{elapsed}s: {frames} frames, {len(audio_data)} samples")
                    last_report = elapsed
        except socket.timeout:
            continue

    sock.close()

    # 保存WAV
    if audio_data:
        duration = len(audio_data) / SAMPLE_RATE
        print(f"Saving {len(audio_data)} samples ({duration:.2f}s)...")

        with wave.open(args.save, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(struct.pack("<" + "h" * len(audio_data), *audio_data))

        print(f"Saved to {args.save}")
    else:
        print("No data received!")


if __name__ == "__main__":
    main()