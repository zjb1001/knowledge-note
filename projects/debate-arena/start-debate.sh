#!/bin/bash
# Debate Arena 一键启动脚本

echo "🎙️  Debate Arena - 多 Agent 辩论系统"
echo "======================================"
echo ""

# 加载 Claude Code + 智谱配置
source ~/.claude/env.sh 2>/dev/null || {
    echo "⚠️  未找到 Claude Code 配置"
    echo "请先运行: ./setup-claude-zhipu.sh"
    exit 1
}

echo "✅ 已加载配置: Model = $ANTHROPIC_MODEL"
echo ""

# 默认辩题
DEFAULT_TOPIC="人工智能是否会取代人类工作"

# 获取辩题
TOPIC="${1:-$DEFAULT_TOPIC}"

echo "📝 辩题: $TOPIC"
echo ""

# 运行辩论
python3 debate.py --topic "$TOPIC" --rounds 3

echo ""
echo "✅ 辩论结束！"
echo ""
echo "使用 GStack 命令分析辩论:"
echo "  /plan debate/正方      - 分析正方策略"
echo "  /plan debate/反方      - 分析反方策略"
echo "  /review debate/逻辑    - 审查论证逻辑"
