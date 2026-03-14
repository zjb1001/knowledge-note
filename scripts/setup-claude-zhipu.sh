#!/bin/bash
# Claude Code + 智谱 GLM-4.7 配置脚本
# 利用甘特图中的 Token 进行配置

set -e

echo "🚀 Claude Code + 智谱 GLM-4.7 配置向导"
echo "=========================================="
echo ""

# 从甘特图获取的智谱 API 配置
ZHIPU_API_KEY="xxx"
ZHIPU_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
ZHIPU_MODEL="glm-4.7"

echo "📋 配置信息:"
echo "  API Key: ${ZHIPU_API_KEY:0:10}...${ZHIPU_API_KEY: -5}"
echo "  Base URL: $ZHIPU_BASE_URL"
echo "  Model: $ZHIPU_MODEL"
echo ""

# 创建配置目录
mkdir -p ~/.claude
mkdir -p ~/.claude-code-router

echo "🔧 创建 Claude Code 配置文件..."

# 创建 Claude Code settings.json
cat > ~/.claude/settings.json << EOF
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "$ZHIPU_API_KEY",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.7",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7",
    "API_TIMEOUT_MS": "300000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
  },
  "preferredLanguage": "zh",
  "allowAnonymousTelemetry": false
}
EOF

echo "  ✓ ~/.claude/settings.json"

# 创建环境变量导出脚本
cat > ~/.claude/env.sh << EOF
#!/bin/bash
# Claude Code 环境变量配置
export ANTHROPIC_API_KEY="$ZHIPU_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$ZHIPU_API_KEY"
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_MODEL="glm-4.7"
export ANTHROPIC_SMALL_FAST_MODEL="glm-4.7"
export API_TIMEOUT_MS="300000"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

echo "Claude Code 环境变量已加载"
echo "Model: glm-4.7 (智谱)"
EOF

chmod +x ~/.claude/env.sh
echo "  ✓ ~/.claude/env.sh"

# 创建 Claude Code Router 配置
cat > ~/.claude-code-router/config.json << EOF
{
  "LOG": true,
  "LOG_LEVEL": "info",
  "CLAUDE_PATH": "",
  "HOST": "127.0.0.1",
  "PORT": 3456,
  "APIKEY": "",
  "API_TIMEOUT_MS": "300000",
  "PROXY_URL": "",
  "transformers": [],
  "Providers": [
    {
      "name": "zhipu",
      "api_base_url": "https://open.bigmodel.cn/api/paas/v4",
      "api_key": "$ZHIPU_API_KEY",
      "models": ["glm-4.7", "glm-4", "glm-4v"]
    }
  ],
  "Router": {
    "default": "zhipu,glm-4.7",
    "background": "zhipu,glm-4.7",
    "thinking": "zhipu,glm-4.7",
    "longContext": "zhipu,glm-4.7",
    "longContextThreshold": 60000
  }
}
EOF

echo "  ✓ ~/.claude-code-router/config.json"

# 添加到 shell 配置
echo ""
echo "📝 配置 Shell 环境..."

SHELL_RC=""
if [ -f ~/.bashrc ]; then
    SHELL_RC="~/.bashrc"
    # 删除旧配置
    sed -i '/# Claude Code 智谱配置/d' ~/.bashrc
    sed -i '/ANTHROPIC_/d' ~/.bashrc
    # 添加新配置
    cat >> ~/.bashrc <> EOF

# Claude Code 智谱配置
export ANTHROPIC_API_KEY="$ZHIPU_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$ZHIPU_API_KEY"
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_MODEL="glm-4.7"
EOF
    fi
fi

if [ -f ~/.zshrc ]; then
    SHELL_RC="~/.zshrc"
    # 删除旧配置
    sed -i '/# Claude Code 智谱配置/d' ~/.zshrc
    sed -i '/ANTHROPIC_/d' ~/.zshrc
    # 添加新配置
    cat >> ~/.zshrc << EOF

# Claude Code 智谱配置
export ANTHROPIC_API_KEY="$ZHIPU_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$ZHIPU_API_KEY"
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_MODEL="glm-4.7"
EOF
    fi
fi

echo "  ✓ 环境变量已添加到 $SHELL_RC"

echo ""
echo "✅ Claude Code + 智谱 GLM-4.7 配置完成！"
echo ""
echo "使用方法:"
echo "  1. 重新加载配置: source ~/.claude/env.sh"
echo "  2. 启动 Claude Code: claude"
echo "  3. 或使用 Router: ccr code"
echo ""
echo "GStack 命令可用:"
echo "  /plan    - CEO产品规划"
echo "  /review  - 代码审查"
echo "  /ship    - 一键发布"
echo "  /qa      - 自动化测试"
echo "  /browser - 浏览器自动化"
echo "  /retro   - 工程复盘"
