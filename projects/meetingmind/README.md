# MeetingMind - 智能会议纪要系统

**类型**: AI驱动的会议纪要自动生成工具  
**技术栈**: Python + 智谱GLM + GStack开发流程  
**驱动方式**: Claude Code + GStack

---

## 🎯 核心功能

1. **音频捕获** - 通过虚拟音频设备录制会议音频
2. **语音识别** - 智谱/Whisper API 实时转录
3. **智能摘要** - LLM自动生成结构化纪要
4. **行动项提取** - 自动识别 Who + What + When

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
export ANTHROPIC_API_KEY="your_key"
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
export ANTHROPIC_MODEL="glm-4.7"

# 3. 设置虚拟音频设备 (macOS)
brew install blackhole-2ch
# 系统设置 → 音频 → 输出 → BlackHole 2ch

# 4. 运行
python main.py
```

---

## 📁 项目结构

```
meetingmind/
├── main.py              # CLI入口
├── core/
│   ├── recorder.py      # 音频录制
│   ├── asr.py           # 语音识别
│   └── summarizer.py    # 纪要生成
├── docs/
│   └── plan-report.md   # CEO规划报告
└── requirements.txt
```

---

## 🎭 系统架构

```
Raw Audio (PCM)
    ↓
[Audio Recorder] → 虚拟音频设备捕获
    ↓
[ASR Engine] → 智谱GLM / Whisper
    ↓
[Summarizer] → 结构化Prompt
    ↓
输出: Markdown纪要 (参会人+议题+行动项)
```

---

## 📋 输出示例

```markdown
# 会议纪要

## 基本信息
- 会议时间: 2026-03-14 14:00
- 参会人员: 张三, 李四, 王五

## 讨论议题
1. **Q2产品规划**: 确认后端API进度80%，前端进度60%
2. **资源协调**: 前端需要设计部高保真原型支持

## 行动项
| 负责人 | 任务描述 | 截止时间 | 状态 |
|--------|----------|----------|------|
| 王五 | 跟进设计部高保真原型 | 2026-03-21 | ⏳ 待完成 |
| 李四 | 完成自动化测试框架搭建 | 2026-03-18 | ⏳ 待完成 |
| 张三 | 协调设计资源 | 2026-03-15 | ⏳ 待完成 |

## 会议总结
会议明确了Q2项目的技术进度和瓶颈，确定了三个关键行动项，主要风险在前端与设计部的协作效率。
```

---

## 🛠️ GStack 开发命令

```bash
# 进入项目
claude

# 规划
/plan meetingmind

# 审查
/review core/summarizer.py

# QA测试
/qa main.py

# 发布
/ship
```

---

## 📅 开发计划

- [x] /plan CEO规划 (完成)
- [x] MVP核心代码 (完成)
- [ ] 实时流式ASR
- [ ] 说话人分离
- [ ] Teams Bot集成
- [ ] 多语言支持

---

*GStack + Claude Code 驱动开发*
