#!/bin/bash
# start.sh - MeetingMind 快速启动脚本
# 用法: ./start.sh [options]

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🎙️  MeetingMind 启动器${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  未检测到虚拟环境，请先运行 ./install.sh${NC}"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 解析参数
MODE="demo"
ARCH_REVIEW=""
PROFILE=""
OUTPUT_DIR="./output"

while [[ $# -gt 0 ]]; do
    case $1 in
        --live)
            MODE="live"
            shift
            ;;
        --arch-review)
            ARCH_REVIEW="--arch-review"
            shift
            ;;
        --profile)
            PROFILE="--profile"
            shift
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --version)
            python3 main.py --version
            exit 0
            ;;
        --help)
            echo "用法: ./start.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --live          录制真实会议音频"
            echo "  --arch-review   包含架构专家评审"
            echo "  --profile       包含性能分析"
            echo "  --output DIR    指定输出目录 (默认: ./output)"
            echo "  --version       显示版本"
            echo "  --help          显示此帮助"
            echo ""
            echo "示例:"
            echo "  ./start.sh                    # 演示模式"
            echo "  ./start.sh --arch-review      # 演示+架构评审"
            echo "  ./start.sh --profile          # 演示+性能分析"
            echo "  ./start.sh --live             # 录制真实会议"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 检查 API Key
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_key_here" ]; then
    echo -e "${YELLOW}⚠️  未配置 API Key，将使用演示模式${NC}"
    MODE="demo"
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 启动
echo -e "${GREEN}🚀 启动 MeetingMind...${NC}"
echo ""

if [ "$MODE" = "live" ]; then
    echo -e "${YELLOW}🔴 将进入录音模式，请确保:${NC}"
    echo "   1. 虚拟音频设备已配置 (如 BlackHole)"
    echo "   2. 系统音频输出已切换到虚拟设备"
    echo ""
    read -p "按回车开始录音，Ctrl+C 结束..."
    echo ""
fi

# 运行主程序
python3 main.py \
    $ARCH_REVIEW \
    $PROFILE \
    --output-dir "$OUTPUT_DIR"

echo ""
echo -e "${GREEN}✅ 处理完成！${NC}"
echo ""
echo "输出文件:"
ls -1t "$OUTPUT_DIR"/meeting_minutes_*.md 2>/dev/null | head -1 | xargs -I {} echo "   📄 {}"
ls -1t "$OUTPUT_DIR"/evaluation_report_*.md 2>/dev/null | head -1 | xargs -I {} echo "   📊 {}"
ls -1t "$OUTPUT_DIR"/architecture_review_*.md 2>/dev/null | head -1 | xargs -I {} echo "   🏛️  {}"
ls -1t "$OUTPUT_DIR"/performance_report_*.md 2>/dev/null | head -1 | xargs -I {} echo "   🚀  {}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
