#!/bin/bash
# Debate Arena 启动脚本

echo "🎙️  Debate Arena - AI 辩论赛"
echo "=============================="
echo ""

# 检查环境
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "🔧 加载 Claude Code + 智谱配置..."
    source ~/.claude/env.sh 2>/dev/null || {
        echo "❌ 错误: 未找到配置文件"
        echo "请先运行: ./setup-claude-zhipu.sh"
        exit 1
    }
fi

echo "✅ 配置加载完成"
echo "   Model: $ANTHROPIC_MODEL"
echo "   Base: $ANTHROPIC_BASE_URL"
echo ""

# 默认辩题
TOPIC="${1:-人工智能是否会取代人类工作}"

echo "📝 辩题: $TOPIC"
echo ""

# 运行辩论
python3 main.py --topic "$TOPIC" --rounds 3

echo ""
echo "✅ 辩论结束！"
