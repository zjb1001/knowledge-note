# Debate Arena

**类型**: Multi-Agent AI 辩论系统  
**技术栈**: Python + OpenAI SDK + 智谱 GLM-4.7  
**驱动方式**: Claude Code + GStack 命令

---

## 快速开始

```bash
# 1. 进入项目
cd debate-arena

# 2. 启动辩论（使用默认辩题）
./run.sh

# 3. 或自定义辩题
./run.sh "元宇宙是否是互联网的未来"
```

---

## 三角色 Agent

| 角色 | 职责 | 系统提示词 |
|------|------|-----------|
| **正方** | 支持辩题 | `agents/roles.py` |
| **反方** | 反对辩题 | `agents/roles.py` |
| **主持人** | 把控流程 | `agents/roles.py` |

---

## GStack 开发命令

```bash
# 进入项目
claude

# 规划正方策略
/plan debate/正方

# 规划反方策略  
/plan debate/反方

# 审查代码
/review agents/roles.py
/review core/arena.py

# 测试验证
/qa main.py
```

---

## 项目结构

```
debate-arena/
├── main.py              # CLI 入口
├── run.sh               # 启动脚本
├── api/
│   └── zhipu.py         # 智谱 API 封装
├── agents/
│   ├── agent.py         # Agent 基类
│   └── roles.py         # 三角色定义
├── core/
│   └── arena.py         # 辩论流程管理
└── AGENTS.md            # GStack 配置
```

---

## 辩论流程

1. **开场** - 主持人介绍
2. **立论** - 双方陈述观点
3. **攻辩** - 互相质询两轮
4. **自由辩论** - 多轮交锋
5. **总结** - 双方陈词
6. **点评** - 主持人总结

---

## 环境变量

```bash
export ANTHROPIC_API_KEY="your_zhipu_key"
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
export ANTHROPIC_MODEL="glm-4.7"
```

---

*Claude Code 驱动开发 - GStack 框架*
