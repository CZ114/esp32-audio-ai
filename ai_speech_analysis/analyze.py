#!/usr/bin/env python3
"""
AI Speech Analyzer
语音AI分析工具 - Whisper转文字 + 语速 + 停顿检测 + 关键词提取
"""

import os
import sys
import json
import wave
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
from dotenv import load_dotenv

# 添加ffmpeg到PATH (Windows)
ffmpeg_path = r"C:\ffmpeg\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")

# 加载环境变量
load_dotenv()

# ===== 配置 =====
SAMPLE_RATE = 16000
FRAME_SIZE = 512
VAD_THRESHOLD = 500

# ===== 语音识别 =====
def speech_to_text(audio_file: str, use_local: bool = True, model_size: str = "base") -> dict:
    """Whisper语音转文字"""
    print(f"[1/4] 语音识别...")

    try:
        # 默认使用本地模型
        if use_local:
            import whisper
            model = whisper.load_model(model_size)
            result = model.transcribe(audio_file, language="zh")
            return {
                "text": result["text"],
                "language": result.get("language", "zh"),
                "segments": result.get("segments", [])
            }
        else:
            # 使用API
            import openai
            client = openai.Client()
            with open(audio_file, "rb") as f:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="zh",
                    response_format="verbose_json"
                )
            return {
                "text": result.text,
                "language": "zh",
                "segments": []
            }
    except ImportError as e:
        print(f"  [!] 模型未安装: {e}")
        print(f"  [i] 使用fallback模式")
        return {"text": "", "language": "zh", "segments": []}


# ===== 停顿检测 =====
def detect_pauses(audio_file: str, sample_rate: int = SAMPLE_RATE,
                min_silence_ms: int = 300) -> list:
    """检测说话段和静音段"""
    print(f"[2/4] 停顿检测...")

    try:
        import webrtcvad
        vad = webrtcvad.Vad(2)
    except ImportError:
        print(f"  [!] webrtcvad未安装，使用能量阈值法")
        return energy_based_vad(audio_file, sample_rate)

    # 读取音频
    with wave.open(audio_file, 'rb') as w:
        frames = w.getnframes()
        data = w.readframes(frames)
        audio = np.frombuffer(data, dtype=np.int16)

    frame_size = int(sample_rate * 0.02)  # 20ms
    segments = []
    is_speech = False
    start = 0

    for i in range(0, len(audio), frame_size):
        frame = audio[i:i+frame_size]
        if len(frame) < frame_size:
            break

        # VAD检测
        try:
            speech = vad.is_speech(frame.tobytes(), sample_rate)
        except:
            speech = np.mean(np.abs(frame)) > VAD_THRESHOLD

        if speech != is_speech:
            # 状态变化
            if i > start:
                duration = (i - start) / sample_rate
                if duration >= min_silence_ms / 1000:
                    segments.append({
                        "type": "speech" if is_speech else "silence",
                        "start": start / sample_rate,
                        "end": i / sample_rate,
                        "duration": duration
                    })
            start = i
            is_speech = speech

    # 添加最后一段
    if len(audio) > start:
        segments.append({
            "type": "speech" if is_speech else "silence",
            "start": start / sample_rate,
            "end": len(audio) / sample_rate,
            "duration": (len(audio) - start) / sample_rate
        })

    return segments


def energy_based_vad(audio_file: str, sample_rate: int = SAMPLE_RATE) -> list:
    """能量阈值VAD (fallback)"""
    with wave.open(audio_file, 'rb') as w:
        frames = w.getnframes()
        data = w.readframes(frames)
        audio = np.frombuffer(data, dtype=np.int16)

    frame_size = int(sample_rate * 0.02)
    segments = []
    is_speech = False
    start = 0

    for i in range(0, len(audio), frame_size):
        frame = audio[i:i+frame_size]
        if len(frame) < frame_size:
            break

        energy = np.mean(np.abs(frame))
        speech = energy > VAD_THRESHOLD

        if speech != is_speech:
            if i > start:
                duration = (i - start) / sample_rate
                if duration >= 0.1:
                    segments.append({
                        "type": "speech" if is_speech else "silence",
                        "start": start / sample_rate,
                        "end": i / sample_rate,
                        "duration": duration
                    })
            start = i
            is_speech = speech

    if len(audio) > start:
        segments.append({
            "type": "speech" if is_speech else "silence",
            "start": start / sample_rate,
            "end": len(audio) / sample_rate,
            "duration": (len(audio) - start) / sample_rate
        })

    return segments


# ===== 关键词提取 =====
def extract_keywords(text: str, top_k: int = 5) -> list:
    """提取关键词"""
    print(f"[3/4] 关键词提取...")

    try:
        import jieba
        from collections import Counter
    except ImportError:
        print(f"  [!] jieba未安装")
        return []

    # 停用词
    stopwords = {
        '的', '了', '是', '在', '和', '去', '吧', '吗', '呢',
        '啊', '哦', '这', '那', '我', '你', '他', '她', '它',
        '很', '也', '都', '有', '就', '要', '来', '到', '说'
    }

    # 分词
    words = jieba.lcut(text)
    words = [w for w in words if w not in stopwords and len(w) > 1]

    # 统计词频
    counter = Counter(words)
    return counter.most_common(top_k)


# ===== 统计计算 =====
def calculate_stats(text: str, segments: list, duration: float) -> dict:
    """计算统计数据"""
    print(f"[4/4] 统计计算...")

    # 说话段
    speech_segments = [s for s in segments if s["type"] == "speech"]
    silence_segments = [s for s in segments if s["type"] == "silence"]

    # 说话时长
    speech_duration = sum(s["duration"] for s in speech_segments)
    silence_duration = sum(s["duration"] for s in silence_segments)

    # 语速 (字/分钟)
    word_count = len(list(text)) if text else 0
    speed = int(word_count / duration * 60) if duration > 0 else 0

    return {
        "word_count": word_count,
        "speed": speed,
        "speech_duration": round(speech_duration, 2),
        "silence_duration": round(silence_duration, 2),
        "speech_ratio": round(speech_duration / duration, 2) if duration > 0 else 0,
        "pause_count": len(silence_segments)
    }


# ===== 主函数 =====
def analyze(audio_file: str, use_local: bool = False, model_size: str = "base",
           output: str = None, verbose: bool = False) -> dict:
    """分析音频文件"""

    print(f"\n{'='*50}")
    print(f"AI Speech Analyzer")
    print(f"{'='*50}")
    print(f"文件: {audio_file}")

    # 检查文件
    if not os.path.exists(audio_file):
        print(f"[!] 文件不存在: {audio_file}")
        return None

    # 获取音频时长
    with wave.open(audio_file, 'rb') as w:
        sample_rate = w.getframerate()
        frames = w.getnframes()
        duration = frames / sample_rate

    print(f"时长: {duration:.2f}秒")
    print(f"采样率: {sample_rate}Hz")

    # 1. 语音转文字
    text_result = speech_to_text(audio_file, use_local, model_size)
    text = text_result.get("text", "")

    if text:
        print(f"  [i] 识别结果: {text[:50]}{'...' if len(text) > 50 else ''}")
    else:
        print(f"  [!] 未识别到文字")

    # 2. 停顿检测
    segments = detect_pauses(audio_file, sample_rate)

    # 3. 关键词
    keywords = extract_keywords(text) if text else []

    # 4. 统计
    stats = calculate_stats(text, segments, duration)

    # 构建结果
    result = {
        "file": audio_file,
        "timestamp": datetime.now().isoformat(),
        "sample_rate": sample_rate,
        "duration": round(duration, 2),
        "text": text,
        "segments": segments,
        "keywords": [k[0] for k in keywords],
        "word_count": stats["word_count"],
        "speed": stats["speed"],
        "speech_duration": stats["speech_duration"],
        "silence_duration": stats["silence_duration"],
        "speech_ratio": stats["speech_ratio"],
        "pause_count": stats["pause_count"]
    }

    # 输出
    print(f"\n{'='*50}")
    print(f"分析结果")
    print(f"{'='*50}")
    print(f"文字: {text or '(无)'}")
    print(f"语速: {stats['speed']} 字/分钟")
    print(f"说话比例: {stats['speech_ratio']*100:.0f}%")
    print(f"停顿次数: {stats['pause_count']}")
    if keywords:
        print(f"关键词: {', '.join([k[0] for k in keywords])}")

    # 保存
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[+] 保存到: {output}")

    print(f"{'='*50}\n")

    return result


# ===== 命令行入口 =====
def main():
    parser = argparse.ArgumentParser(
        description="AI Speech Analyzer - 语音AI分析工具"
    )
    parser.add_argument(
        "audio", nargs="?", help="音频文件路径"
    )
    parser.add_argument(
        "-o", "--output", help="输出JSON文件"
    )
    parser.add_argument(
        "--local", action="store_true",
        help="使用本地Whisper模型"
    )
    parser.add_argument(
        "--model", default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="本地模型大小"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="详细输出"
    )

    args = parser.parse_args()

    # 交互模式
    if args.audio is None:
        audio_file = input("音频文件路径: ").strip().strip('"')
        if not audio_file:
            print("用法: python analyze.py <audio.wav>")
            sys.exit(1)
    else:
        audio_file = args.audio

    # 运行分析
    analyze(
        audio_file,
        use_local=args.local or os.getenv("USE_LOCAL_MODEL") == "true",
        model_size=args.model,
        output=args.output,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()