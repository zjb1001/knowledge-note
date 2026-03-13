#!/bin/bash
# WeAgent 多 Agent 任务调度脚本
# 项目：智能底盘与高阶智驾知识库构建

WORKSPACE="/root/.openclaw/workspace/weagent-chassis-ad"
OUTPUT_DIR="$WORKSPACE/output"

echo "========================================"
echo "WeAgent Multi-Agent System Starting..."
echo "========================================"

# 创建输出目录
mkdir -p $OUTPUT_DIR/{01-knowledge-graph,02-system-architecture,03-detailed-design,04-implementation,05-quality-report}

echo ""
echo "[Phase 1] Content Analysis Agent Starting..."
echo "Agent ID: agent-01-analyzer"
echo "Task: 分析培训大纲，提取知识点"
