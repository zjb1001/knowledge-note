#!/usr/bin/env python3
"""
Debate Arena CLI
"""
import argparse
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.arena import DebateArena


def main():
    parser = argparse.ArgumentParser(description='🎙️  Debate Arena - AI 辩论赛')
    parser.add_argument('--topic', '-t', type=str, 
                        default='人工智能是否会取代人类工作',
                        help='辩题 (默认: 人工智能是否会取代人类工作)')
    parser.add_argument('--rounds', '-r', type=int, default=3,
                        help='自由辩论轮数 (默认: 3)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出文件路径')
    
    args = parser.parse_args()
    
    # 检查环境变量
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ 错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        print("请先运行: source ~/.claude/env.sh")
        return 1
    
    print(f"🚀 启动辩论...")
    print(f"📝 辩题: {args.topic}")
    print(f"🔄 自由辩论轮数: {args.rounds}")
    print()
    
    # 创建并启动辩论
    arena = DebateArena(topic=args.topic, rounds=args.rounds)
    arena.start()
    
    # 保存记录
    arena.save_transcript(args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
