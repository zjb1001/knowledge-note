#!/bin/bash
# MeetingMind 启动脚本

echo "🎙️  MeetingMind - 智能会议纪要系统"
echo "======================================"

# 检查环境
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "🔧 加载环境配置..."
    source ~/.claude/env.sh 2>/dev/null || {
        echo "❌ 错误: 未找到配置文件"
        exit 1
    }
fi

echo "✅ 配置加载完成"
echo "   Model: $ANTHROPIC_MODEL"
echo ""

# 检查依赖
python3 -c "import pyaudio" 2>/dev/null || {
    echo "⚠️  未安装 pyaudio，正在安装..."
    pip install pyaudio
}

# 运行
python3 main.py
