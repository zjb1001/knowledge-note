#!/bin/bash
# extract-meetingmind.sh
# 从 knowledge-note 摘取 MeetingMind 项目

# 创建独立项目目录
mkdir -p ~/meetingmind
cd ~/meetingmind

# 复制核心文件
cp /root/.openclaw/workspace/knowledge-note/projects/meetingmind/main.py .
cp /root/.openclaw/workspace/knowledge-note/projects/meetingmind/demo_v2.py .
cp /root/.openclaw/workspace/knowledge-note/projects/meetingmind/requirements.txt .
cp /root/.openclaw/workspace/knowledge-note/projects/meetingmind/.gitignore .
cp /root/.openclaw/workspace/knowledge-note/projects/meetingmind/README.md .

# 复制核心模块
mkdir -p core
cp /root/.openclaw/workspace/knowledge-note/projects/meetingmind/core/*.py core/

# 初始化Git
git init
git add .
git commit -m "Initial commit: MeetingMind extracted from knowledge-note"

echo "✅ MeetingMind 已摘取到 ~/meetingmind"
echo ""
echo "下一步:"
echo "  cd ~/meetingmind"
echo "  pip install -r requirements.txt"
echo "  python demo_v2.py"
