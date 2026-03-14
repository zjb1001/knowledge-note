#!/usr/bin/env python3
"""
MeetingMind - 智能会议纪要系统 (Demo模式)
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.asr import ZhipuASR
from core.summarizer import MeetingSummarizer


def print_banner():
    print("=" * 70)
    print("🎙️  MeetingMind - 智能会议纪要系统 [Demo模式]")
    print("=" * 70)
    print()


def main():
    print_banner()
    
    # 检查环境
    api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        return 1
    
    print("⚙️ 初始化组件...")
    asr = ZhipuASR()
    summarizer = MeetingSummarizer()
    
    print(f"✅ 配置完成 | Model: {os.getenv('ANTHROPIC_MODEL', 'glm-4.7')}")
    print()
    
    # 模拟获取转录文本
    print("📝 使用模拟会议文本进行演示...")
    transcript = asr._mock_transcript()
    print(f"✅ 转录完成，共 {len(transcript)} 字符")
    print()
    
    # 生成纪要
    print("🧠 正在调用智谱GLM生成会议纪要...")
    print("   (使用结构化Prompt提取行动项)")
    print()
    
    minutes = summarizer.generate(transcript)
    
    # 保存输出
    output_file = f"meeting_minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(minutes)
    
    # 显示结果
    print("=" * 70)
    print("📋 生成的会议纪要:")
    print("=" * 70)
    print()
    print(minutes)
    print()
    print("=" * 70)
    print(f"💾 已保存至: {output_file}")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
