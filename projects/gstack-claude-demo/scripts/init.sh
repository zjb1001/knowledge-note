#!/bin/bash
# 项目初始化脚本

echo "初始化 $PROJECT_NAME 项目..."

# 初始化 git
git init
git add .
git commit -m "Initial commit: GStack + Claude Code + 智谱 GLM-4"

echo "✅ 项目初始化完成"
echo "启动 Claude Code: claude"
