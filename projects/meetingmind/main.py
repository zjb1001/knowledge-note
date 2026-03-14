#!/usr/bin/env python3
"""
MeetingMind - 智能会议纪要系统
MVP版本：本地音频录制 + 智谱ASR + 结构化纪要
"""
import os
import sys
import wave
import json
import queue
import tempfile
import threading
from datetime import datetime
from typing import List, Dict, Optional
# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pyaudio
    from core.recorder import AudioRecorder
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False
    print("⚠️  未安装 pyaudio，使用模拟模式运行")

from core.asr import ZhipuASR
from core.summarizer import MeetingSummarizer


def print_banner():
    """打印启动横幅"""
    print("=" * 70)
    print("🎙️  MeetingMind - 智能会议纪要系统")
    print("=" * 70)
    print("\n功能:")
    print("  1. 录制会议音频 (虚拟音频设备)")
    print("  2. 语音识别 (智谱 GLM-4)")
    print("  3. 自动生成结构化纪要")
    print("\n使用说明:")
    print("  - 请将系统音频输出设置为虚拟音频设备 (如VB-Cable)")
    print("  - 开始录音后，正常进行会议")
    print("  - 结束录音后自动生成纪要")
    print("=" * 70)
    print()


def main():
    print_banner()
    
    # 检查环境
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ 错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        print("请先运行: source ~/.claude/env.sh")
        return 1
    
    # 初始化组件
    recorder = AudioRecorder()
    asr = ZhipuASR()
    summarizer = MeetingSummarizer()
    
    # 用户确认
    print("⚙️ 配置检查完成")
    print(f"   ASR模型: {os.getenv('ANTHROPIC_MODEL', 'glm-4.7')}")
    print()
    
    input("🎤 请将音频输出设置为虚拟音频设备，按回车开始录音...")
    
    # 开始录音
    print("\n🔴 录音中... (按 Ctrl+C 停止)")
    audio_file = recorder.record_until_stop()
    
    if not audio_file:
        print("❌ 录音失败")
        return 1
    
    print(f"\n✅ 录音完成: {audio_file}")
    
    # 语音识别
    print("\n📝 正在进行语音识别...")
    transcript = asr.transcribe(audio_file)
    
    if not transcript:
        print("❌ 识别失败")
        return 1
    
    print(f"✅ 识别完成，共 {len(transcript)} 字符")
    
    # 生成纪要
    print("\n🧠 正在生成会议纪要...")
    minutes = summarizer.generate(transcript)
    
    # 保存输出
    output_file = f"meeting_minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(minutes)
    
    print(f"\n✅ 会议纪要已保存: {output_file}")
    print("\n" + "=" * 70)
    print("📋 会议纪要预览:")
    print("=" * 70)
    print(minutes[:500] + "..." if len(minutes) > 500 else minutes)
    
    # 清理临时文件
    os.unlink(audio_file)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
