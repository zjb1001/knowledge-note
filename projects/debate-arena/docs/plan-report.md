## /plan debate-arena - CEO 产品规划报告

**规划时间**: 2026-03-14  
**规划者**: CEO/产品规划专家  
**目标**: 基于 AGENTS.md 三角色定义，规划辩论系统 MVP

---

### 核心洞察

辩论系统的本质是：**三个专业角色围绕一个主题进行结构化讨论**。不是简单的问答，而是有流程、有策略、有博弈的对抗性对话。

**关键成功因素**:
1. 角色分工清晰（正方/反方/主持人）
2. 流程控制严格（时间、节奏）
3. API 调用稳定（智谱 GLM-4.7）
4. 历史记录完整（可追溯、可复盘）

---

### MVP 功能范围

**必须实现**:
- [x] 三 Agent 角色定义（AGENTS.md 已完成）
- [ ] Agent 类实现（基类+三角色）
- [ ] 智谱 API 调用封装
- [ ] 六阶段辩论流程
- [ ] 辩论记录保存

**延后实现**:
- Web 界面
- 实时流式输出
- 辩论评分系统
- 多轮辩论记忆

---

### 核心模块设计

```
debate-arena/
├── agents/
│   ├── base.py          # DebateAgent 基类
│   ├── pro.py           # ProAgent 正方
│   ├── con.py           # ConAgent 反方
│   └── moderator.py     # ModeratorAgent 主持人
├── api/
│   └── zhipu.py         # 智谱 GLM-4.7 封装
├── core/
│   └── arena.py         # DebateArena 管理类
└── cli.py               # 命令行入口
```

---

### API 接入方案

**智谱 GLM-4.7**:
```python
client = OpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

response = client.chat.completions.create(
    model="glm-4.7",
    messages=[
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.7,
    max_tokens=2000
)
```

---

### 开发优先级

| 优先级 | 模块 | 工时 | 依赖 |
|--------|------|------|------|
| P0 | API 封装 | 30min | 无 |
| P0 | Agent 基类 | 30min | API 封装 |
| P0 | 三角色实现 | 30min | Agent 基类 |
| P0 | 辩论流程 | 30min | 三角色 |
| P1 | CLI 入口 | 15min | 辩论流程 |
| P1 | 记录保存 | 15min | 辩论流程 |

**总工时**: ~2.5 小时

---

### 下一步行动

- [ ] CEO 规划完成 ✓
- [ ] 工程经理审查设计
- [ ] 开发实现
- [ ] QA 测试验证
- [ ] 发布上线

---

*规划完成 - 进入开发阶段*
