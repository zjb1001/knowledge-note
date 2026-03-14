# 辩论应用 (Debate Arena)

**项目类型**: Multi-Agent 辩论系统  
**技术栈**: GStack + Claude Code + 智谱 GLM-4.7  
**创建时间**: 2026-03-14

---

## 项目概述

一个基于多 Agent 的辩论应用，支持三个角色：
- **正方 Agent**: 维护辩题，提供支持论据
- **反方 Agent**: 反对辩题，提供反驳论据  
- **主持人 Agent**: 把控节奏，引导讨论，总结陈词

---

## 快速开始

```bash
# 进入项目
cd /root/.openclaw/workspace/projects/debate-arena

# 加载配置
source ~/.claude/env.sh

# 启动辩论
python debate.py --topic "人工智能是否会取代人类工作"
```

---

## GStack 命令

```
/plan debate/正方      - 规划正方论点
/plan debate/反方      - 规划反方论点
/review debate/逻辑    - 审查辩论逻辑
/qa debate/流程        - 测试辩论流程
```

---

## 辩论流程

1. **开场** - 主持人介绍辩题和规则
2. **立论** - 正方/反方依次陈述观点
3. **攻辩** - 双方互相质疑
4. **自由辩论** - 多轮交锋
5. **总结** - 双方总结陈词
6. **点评** - 主持人点评

---

## Agent 配置

- **正方**: Claude Code + 智谱 GLM-4.7 (Pro方角色)
- **反方**: Claude Code + 智谱 GLM-4.7 (Con方角色)
- **主持人**: Claude Code + 智谱 GLM-4.7 (Moderator角色)

---

*基于 GStack Multi-Agent 框架构建*
