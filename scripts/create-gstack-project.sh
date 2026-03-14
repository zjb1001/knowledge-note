#!/bin/bash
# GStack + Claude Code + 智谱 GLM-4 项目创建脚本

set -e

PROJECT_NAME="${1:-my-project}"
PROJECT_DIR="/root/.openclaw/workspace/projects/$PROJECT_NAME"

echo "🚀 GStack + Claude Code + 智谱 GLM-4 项目创建"
echo "=============================================="
echo ""
echo "项目名称: $PROJECT_NAME"
echo "项目路径: $PROJECT_DIR"
echo ""

# 加载智谱配置
source ~/.claude/env.sh 2>/dev/null || {
    echo "⚠️  未找到 Claude Code 配置，先运行 setup-claude-zhipu.sh"
    exit 1
}

# 创建项目目录
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "📁 创建项目结构..."

# 创建 GStack 项目结构
mkdir -p {docs/{planning,design,requirements,api},src,tests,scripts}

# 创建 README
cat > README.md << EOF
# $PROJECT_NAME

**项目类型**: GStack + Claude Code + 智谱 GLM-4  
**创建时间**: $(date '+%Y-%m-%d')

## GStack 命令

| 命令 | 功能 |
|------|------|
| /plan | CEO产品规划 |
| /review | 工程经理代码审查 |
| /ship | 发布经理一键发布 |
| /qa | QA工程师自动化测试 |
| /browser | 浏览器自动化 |
| /retro | 工程复盘 |

## 快速开始

\`\`\`bash
# 启动 Claude Code
claude

# 在 Claude Code 中使用 GStack 命令
/plan 分析项目需求
/review 审查代码
/ship 准备发布
\`\`\`

## 智谱 GLM-4 配置

- API: 智谱大模型
- Model: glm-4
- Base URL: https://open.bigmodel.cn/api/anthropic

---
*自动生成于 $(date '+%Y-%m-%d %H:%M')*
EOF

# 创建 GStack 配置
cat > AGENTS.md << 'EOF'
# GStack 专家团队配置

## 斜杠命令

### /plan - CEO产品规划专家
从创始人视角分析需求，提供MVP/标准版/10星级方案

### /review - 工程经理代码审查
代码质量、架构设计、安全审计

### /ship - 发布经理一键部署
发布前检查、风险评估、回滚策略

### /qa - QA工程师自动化测试
测试用例设计、边界探索、性能验证

### /browser - 浏览器自动化专家
UI自动化、视觉回归、跨浏览器测试

### /retro - 工程复盘专家
事后复盘、根因分析、流程改进

## 使用方式

在 Claude Code 中直接输入斜杠命令：
```
/plan 我要做一个智能客服系统
/review 请审查这个PR
/ship 发布v1.0.0
```
EOF

# 创建项目初始化脚本
cat > scripts/init.sh << 'EOF'
#!/bin/bash
# 项目初始化脚本

echo "初始化 $PROJECT_NAME 项目..."

# 初始化 git
git init
git add .
git commit -m "Initial commit: GStack + Claude Code + 智谱 GLM-4"

echo "✅ 项目初始化完成"
echo "启动 Claude Code: claude"
EOF

chmod +x scripts/init.sh

# 创建示例规划文档
cat > docs/planning/sprint-1.md << EOF
# Sprint 1 规划

**项目**: $PROJECT_NAME  
**周期**: 1周  
**目标**: 完成核心功能原型

## 任务清单

- [ ] T1: 需求分析
- [ ] T2: 架构设计
- [ ] T3: 核心功能开发
- [ ] T4: 测试验证
- [ ] T5: 文档整理

## GStack 命令

\`\`\`
/plan $PROJECT_NAME
/review src/
/qa tests/
/ship v0.1.0
\`\`\`
EOF

echo "✅ 项目创建完成！"
echo ""
echo "项目路径: $PROJECT_DIR"
echo ""
echo "下一步:"
echo "  cd $PROJECT_DIR"
echo "  ./scripts/init.sh"
echo "  claude"
echo ""
echo "在 Claude Code 中使用:"
echo "  /plan 分析项目需求"
