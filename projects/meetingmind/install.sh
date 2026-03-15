#!/bin/bash
# install.sh - MeetingMind 一键安装脚本
# 用法: ./install.sh

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🎙️  MeetingMind 安装程序"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未检测到 Python3"
    echo "   请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
echo "✅ 检测到 Python $PYTHON_VERSION"

# 创建虚拟环境
echo ""
echo "📦 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ 虚拟环境已创建"
else
    echo "   ⚠️  虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
echo ""
echo "🚀 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "⬆️  升级 pip..."
pip install --quiet --upgrade pip

# 安装依赖
echo ""
echo "📥 安装依赖..."
pip install --quiet -r requirements.txt
echo "   ✅ 依赖安装完成"

# 创建 .env 文件
echo ""
echo "🔧 配置环境..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# MeetingMind 配置文件
# 请填写你的 API Key

ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ANTHROPIC_MODEL=glm-4.7
EOF
    echo "   ✅ 已创建 .env 模板文件"
    echo "   ⚠️  请编辑 .env 文件，填入你的 API Key"
else
    echo "   ⚠️  .env 文件已存在，跳过创建"
fi

# 创建输出目录
echo ""
echo "📁 创建输出目录..."
mkdir -p output
echo "   ✅ 输出目录已创建"

# 测试运行
echo ""
echo "🧪 测试运行..."
python3 main.py --version
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✅ 安装完成！"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "使用方法:"
echo "   1. 编辑 .env 文件，填入 API Key"
echo "   2. source venv/bin/activate"
echo "   3. python3 main.py"
echo ""
echo "快速开始:"
echo "   ./start.sh          # 启动演示"
echo "   ./start.sh --live   # 录制真实会议"
echo ""
echo "═══════════════════════════════════════════════════════════════"
