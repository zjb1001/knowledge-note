# Debate Arena - Claude Code 驱动开发指令

**目标**: 用 Claude Code + GStack 命令完成辩论系统开发

---

## 启动 Claude Code

```bash
cd /root/.openclaw/workspace/projects/debate-arena

# 加载智谱配置
source ~/.claude/env.sh

# 启动 ccgo (Claude Code 国内版)
ccgo
```

---

## GStack 开发流程

### Step 1: /plan - CEO 产品规划

在 Claude Code 中输入:
```
/plan debate-arena

请基于 AGENTS.md 中的三角色定义，规划辩论系统的:
1. MVP 功能范围
2. 核心模块设计
3. API 接入方案(智谱 GLM-4.7)
4. 开发优先级
```

**预期输出**:
- 产品规划报告
- 模块拆分建议
- 技术选型确认

---

### Step 2: 实现核心架构

在 Claude Code 中输入:
```
根据 AGENTS.md 中的角色定义，实现:

1. DebateAgent 基类
2. ProAgent/ConAgent/ModeratorAgent 三角色
3. DebateArena 管理类
4. 智谱 API 调用封装

要求:
- 读取 debate-config.json 配置
- 支持真实 API 调用
- 完整类型注解
```

**Claude Code 会自动**:
- 读取 AGENTS.md 理解角色
- 读取 debate-config.json 获取配置
- 生成完整的 Python 代码
- 处理 API 调用和错误处理

---

### Step 3: /review - 代码审查

在 Claude Code 中输入:
```
/review debate.py

请审查刚生成的代码:
1. 逻辑是否完整
2. API 调用是否正确
3. 是否有错误处理
4. 是否符合 GStack 规范
```

**Claude Code 会**:
- 自审代码
- 标记 🔴🟡🟢 问题
- 提供修复建议
- 自动修复简单问题

---

### Step 4: /qa - 测试验证

在 Claude Code 中输入:
```
/qa debate.py

请生成测试用例:
1. 单元测试
2. 集成测试
3. API 调用测试
4. 边界条件测试
```

---

### Step 5: /ship - 发布

在 Claude Code 中输入:
```
/ship v1.0.0

准备发布:
1. 代码最终检查
2. 文档完善
3. Git 提交
4. 推送到远程
```

---

## 关键指令模板

### 初始化项目
```
请读取当前目录下的 AGENTS.md，理解三个 Agent 角色的定义。
然后基于这些角色，实现一个完整的辩论系统。
```

### 实现 API 调用
```
请实现智谱 GLM-4.7 的 API 调用封装:
- Base URL: https://open.bigmodel.cn/api/paas/v4
- Model: glm-4.7
- API Key 从环境变量读取

实现一个 generate_response(system_prompt, user_prompt) 函数。
```

### 完善辩论流程
```
请完善 DebateArena 类，实现完整的 6 阶段辩论流程:
1. opening - 开场
2. statement - 立论
3. attack - 攻辩
4. free_debate - 自由辩论
5. summary - 总结
6. closing - 点评

每个阶段都要调用对应的 Agent 生成内容。
```

---

## 直接开始

现在执行:

```bash
cd /root/.openclaw/workspace/projects/debate-arena
source ~/.claude/env.sh
ccgo

# 然后在 ccgo 中输入:
请读取 AGENTS.md，基于三角色定义实现完整的辩论系统。
使用智谱 GLM-4.7 API。
```

---

*Claude Code 驱动开发 - 无需手动写代码*
